import os
import logging
from typing import Dict, Any, List
import pypdf
import docx
import pdfplumber
from io import BytesIO
from app.core.config import settings

logger = logging.getLogger(__name__)


class DocumentProcessor:
    def __init__(self):
        self.supported_types = ['pdf', 'docx', 'txt']
    
    def extract_text(self, file_content: bytes, filename: str, file_type: str) -> str:
        try:
            if file_type == 'pdf':
                return self._extract_from_pdf(file_content, filename)
            elif file_type == 'docx':
                return self._extract_from_docx(file_content, filename)
            elif file_type == 'txt':
                return self._extract_from_txt(file_content, filename)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
        except Exception as e:
            logger.error(f"Error processing {filename}: {e}")
            raise
    
    def _extract_from_pdf(self, file_content: bytes, filename: str) -> str:
        try:
            text_parts = []
            
            try:
                with pdfplumber.open(BytesIO(file_content)) as pdf:
                    for i, page in enumerate(pdf.pages):
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append(f"Page {i + 1}\n{page_text}")
            except Exception as e:
                logger.warning(f"pdfplumber failed, trying pypdf: {e}")
            
            if not text_parts:
                pdf_reader = pypdf.PdfReader(BytesIO(file_content))
                for i, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(f"Page {i + 1}\n{page_text}")
            
            full_text = "\n\n".join(text_parts)
            
            if not full_text.strip():
                raise ValueError("No text could be extracted from PDF")
            
            return full_text
            
        except Exception as e:
            logger.error(f"Error extracting PDF {filename}: {e}")
            raise
    
    def _extract_from_docx(self, file_content: bytes, filename: str) -> str:
        try:
            doc = docx.Document(BytesIO(file_content))
            text_parts = []
            
            for para in doc.paragraphs:
                if para.text.strip():
                    text_parts.append(para.text)
            
            text = "\n".join(text_parts)
            
            if not text.strip():
                raise ValueError("No text could be extracted from DOCX")
            
            return text
            
        except Exception as e:
            logger.error(f"Error extracting DOCX {filename}: {e}")
            raise
    
    def _extract_from_txt(self, file_content: bytes, filename: str) -> str:
        try:
            text = file_content.decode('utf-8')
            
            if not text.strip():
                raise ValueError("Text file is empty")
            
            return text
            
        except UnicodeDecodeError:
            try:
                text = file_content.decode('latin-1')
                return text
            except Exception as e:
                logger.error(f"Error decoding TXT {filename}: {e}")
                raise
        except Exception as e:
            logger.error(f"Error extracting TXT {filename}: {e}")
            raise
    
    def get_file_type(self, filename: str) -> str:
        ext = filename.lower().split('.')[-1]
        
        if ext not in self.supported_types:
            raise ValueError(f"Unsupported file extension: {ext}. Supported types: {self.supported_types}")
        
        return ext
    
    def validate_file_size(self, file_size: int) -> bool:
        if file_size > settings.max_file_size:
            raise ValueError(f"File too large. Maximum size: {settings.max_file_size / (1024*1024):.0f}MB")
        return True


document_processor = DocumentProcessor()
