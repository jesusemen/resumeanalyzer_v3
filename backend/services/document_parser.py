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
            import PyPDF2
            
            pdf_reader = PyPDF2.PdfReader(BytesIO(file_content))
            text = ""
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                else:
                    logger.warning(f"No text extracted from PDF page {page_num}")
            
            final_text = text.strip()
            if not final_text:
                logger.error("Extracted PDF text is empty")
                return None
            return final_text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return None
    
    @staticmethod
    def extract_text_from_docx(file_content: bytes) -> Optional[str]:
        """Extract text from DOCX file content"""
        try:
            from io import BytesIO
            import docx
            
            doc = docx.Document(BytesIO(file_content))
            text = ""
            for paragraph in doc.paragraphs:
                if paragraph.text:
                    text += paragraph.text + "\n"
            
            final_text = text.strip()
            if not final_text:
                logger.error("Extracted DOCX text is empty")
                return None
            return final_text
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {e}")
            return None
    
    @staticmethod
    def extract_text_from_doc(file_content: bytes) -> Optional[str]:
        """Extract text from legacy DOC file content"""
        try:
            # Legacy .doc files are binary. Simple decoding is unreliable.
            # We try to extract any readable strings as a fallback.
            import re
            text = file_content.decode('utf-8', errors='ignore')
            # Filter out non-printable characters to get some readable text
            clean_text = re.sub(r'[^\x20-\x7E\x0A\x0D]', ' ', text)
            # Remove multiple spaces
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
            
            if len(clean_text) < 20: # Arbitrary small limit for "meaningful" text
                logger.error("Extracted DOC text is too short or empty")
                return None
            return clean_text
        except Exception as e:
            logger.error(f"Error extracting text from DOC: {e}")
            return None
    
    @classmethod
    def extract_text(cls, file_content: bytes, filename: str) -> Optional[str]:
        """Extract text from file based on extension"""
        filename_lower = filename.lower()
        logger.info(f"Extracting text from: {filename}")
        
        try:
            if filename_lower.endswith('.pdf'):
                return cls.extract_text_from_pdf(file_content)
            elif filename_lower.endswith('.docx'):
                return cls.extract_text_from_docx(file_content)
            elif filename_lower.endswith('.doc'):
                return cls.extract_text_from_doc(file_content)
            else:
                logger.error(f"Unsupported file format: {filename}")
                return None
        except Exception as e:
            logger.error(f"Unexpected error in extract_text for {filename}: {e}")
            return None