import PyPDF2
import docx
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class DocumentParser:
    @staticmethod
    def extract_text_from_pdf(file_content: bytes) -> Optional[str]:
        """Extract text from PDF file content"""
        try:
            from io import BytesIO
            pdf_reader = PyPDF2.PdfReader(BytesIO(file_content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return None
    
    @staticmethod
    def extract_text_from_docx(file_content: bytes) -> Optional[str]:
        """Extract text from DOCX file content"""
        try:
            from io import BytesIO
            doc = docx.Document(BytesIO(file_content))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {e}")
            return None
    
    @staticmethod
    def extract_text_from_doc(file_content: bytes) -> Optional[str]:
        """Extract text from DOC file content - simplified approach"""
        try:
            # For DOC files, we'll try to convert to string
            # This is a simplified approach - in production, you might want to use python-docx2txt
            text = file_content.decode('utf-8', errors='ignore')
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from DOC: {e}")
            return None
    
    @classmethod
    def extract_text(cls, file_content: bytes, filename: str) -> Optional[str]:
        """Extract text from file based on extension"""
        filename_lower = filename.lower()
        
        if filename_lower.endswith('.pdf'):
            return cls.extract_text_from_pdf(file_content)
        elif filename_lower.endswith('.docx'):
            return cls.extract_text_from_docx(file_content)
        elif filename_lower.endswith('.doc'):
            return cls.extract_text_from_doc(file_content)
        else:
            logger.error(f"Unsupported file format: {filename}")
            return None