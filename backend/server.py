from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException, Form, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
import asyncio

# Import custom services
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from services.document_parser import DocumentParser
from services.resume_analyzer import ResumeAnalyzer

# Import auth modules
from auth.models import UserCreate, UserLogin, UserResponse, UserInDB, Token
from auth.auth_handler import verify_password, get_password_hash, create_access_token
from auth.dependencies import get_current_user




ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.getenv('MONGO_URL')
if not mongo_url:
    raise ValueError("MONGO_URL environment variable is required")
client = AsyncIOMotorClient(mongo_url)
db = client[os.getenv('DB_NAME', 'resume_analyzer')]

# Create the main app
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://resume-analyzer-frontend-8pd5.onrender.com",
        "https://resumeanalyzer-v3-1.onrender.com",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Initialize services
document_parser = DocumentParser()
resume_analyzer = ResumeAnalyzer()

# Models
class AnalysisResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    job_description_filename: str
    total_resumes: int
    candidates: List[dict]
    no_match: bool
    analysis_date: datetime = Field(default_factory=datetime.utcnow)

class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

# Auth routes
@api_router.post("/auth/register", response_model=Token)
async def register(user_data: UserCreate):
    """Register a new user"""
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user_in_db = UserInDB(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password
    )
    
    # Insert user into database
    await db.users.insert_one(user_in_db.dict())
    
    # Create access token
    access_token = create_access_token(data={"sub": user_in_db.id})
    
    # Return token and user info
    user_response = UserResponse(
        id=user_in_db.id,
        email=user_in_db.email,
        full_name=user_in_db.full_name,
        created_at=user_in_db.created_at,
        is_active=user_in_db.is_active
    )
    
    return Token(access_token=access_token, user=user_response)

@api_router.post("/auth/login", response_model=Token)
async def login(user_data: UserLogin):
    """Login user"""
    # Find user by email
    user = await db.users.find_one({"email": user_data.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    user_in_db = UserInDB(**user)
    
    # Verify password
    if not verify_password(user_data.password, user_in_db.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user_in_db.id})
    
    # Return token and user info
    user_response = UserResponse(
        id=user_in_db.id,
        email=user_in_db.email,
        full_name=user_in_db.full_name,
        created_at=user_in_db.created_at,
        is_active=user_in_db.is_active
    )
    
    return Token(access_token=access_token, user=user_response)

@api_router.get("/user/profile", response_model=UserResponse)
async def get_user_profile(current_user: UserInDB = Depends(get_current_user)):
    """Get current user profile"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        created_at=current_user.created_at,
        is_active=current_user.is_active
    )

# Existing routes
@api_router.get("/")
async def root():
    return {"message": "Resume Analyzer API Ready"}

@api_router.get("/health")
async def health_check():
    """Check database connection status"""
    try:
        # Ping the database
        await client.admin.command('ping')
        return {
            "status": "ok",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# Protected resume analysis endpoint
@api_router.post("/analyze-resumes")
async def analyze_resumes(
    job_description: UploadFile = File(...),
    resumes: List[UploadFile] = File(...),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Analyze resumes against job description (Protected endpoint)
    """
    try:
        # Validate inputs
        if not job_description.filename.lower().endswith(('.pdf', '.doc', '.docx')):
            raise HTTPException(
                status_code=400, 
                detail="Job description must be a PDF, DOC, or DOCX file"
            )
        
        if len(resumes) < 5:
            raise HTTPException(
                status_code=400, 
                detail="At least 5 resumes are required for analysis"
            )
        
        if len(resumes) > 30:
            raise HTTPException(
                status_code=400, 
                detail="Maximum 30 resumes can be processed at once"
            )
        
        # Validate resume file types
        for resume in resumes:
            if not resume.filename.lower().endswith(('.pdf', '.doc', '.docx')):
                raise HTTPException(
                    status_code=400, 
                    detail=f"Resume {resume.filename} must be a PDF, DOC, or DOCX file"
                )
        
        # Extract job description text
        job_content = await job_description.read()
        job_text = document_parser.extract_text(job_content, job_description.filename)
        
        if not job_text:
            raise HTTPException(
                status_code=400, 
                detail="Could not extract text from job description"
            )
        
        # Process resumes
        resume_data = []
        for resume in resumes:
            resume_content = await resume.read()
            resume_text = document_parser.extract_text(resume_content, resume.filename)
            
            if resume_text:
                # Extract contact info from resume
                contact_info = resume_analyzer._extract_contact_info(resume_text)
                resume_data.append({
                    'name': contact_info['name'],
                    'email': contact_info['email'],
                    'phone': contact_info['phone'],
                    'content': resume_text,
                    'filename': resume.filename
                })
        
        logging.info(f"Processing {len(resume_data)} valid resumes for user {current_user.id}")
        
        if len(resume_data) < 5:
            raise HTTPException(
                status_code=400, 
                detail=f"Only {len(resume_data)} resumes could be processed. At least 5 are required."
            )
        
        # Analyze resumes using AI
        analysis_results = await resume_analyzer.analyze_batch_resumes(job_text, resume_data)
        
        # Save results to database
        result_obj = AnalysisResult(
            user_id=current_user.id,
            job_description_filename=job_description.filename,
            total_resumes=len(resume_data),
            candidates=analysis_results['candidates'],
            no_match=analysis_results['noMatch']
        )
        
        await db.analysis_results.insert_one(result_obj.dict())
        
        return {
            "success": True,
            "message": "Analysis completed successfully",
            "data": {
                "candidates": analysis_results['candidates'],
                "noMatch": analysis_results['noMatch'],
                "totalAnalyzed": len(resume_data),
                "analysisDate": result_obj.analysis_date.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error analyzing resumes: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

# Get analysis history (protected)
@api_router.get("/analysis-history")
async def get_analysis_history(current_user: UserInDB = Depends(get_current_user)):
    """Get user's past analysis results"""
    try:
        results = await db.analysis_results.find(
            {"user_id": current_user.id}
        ).sort("analysis_date", -1).to_list(10)
        
        return [
            {
                "id": result["id"],
                "job_description_filename": result["job_description_filename"],
                "total_resumes": result["total_resumes"],
                "analysis_date": result["analysis_date"],
                "candidates_count": len(result["candidates"])
            }
            for result in results
        ]
    except Exception as e:
        logging.error(f"Error fetching analysis history: {e}")
        raise HTTPException(status_code=500, detail="Error fetching analysis history")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
