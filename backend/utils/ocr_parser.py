"""
OCR and PDF parsing utilities for extracting data from documents
"""
import pdfplumber
from pathlib import Path
import pandas as pd
from typing import List, Dict, Optional, Union
import logging
import io
import requests

try:
    from paddleocr import PaddleOCR
    PADDLE_AVAILABLE = True
except ImportError:
    PADDLE_AVAILABLE = False
    logging.warning("PaddleOCR not available. OCR functionality will be limited.")

from PIL import Image

logger = logging.getLogger(__name__)


class PDFParser:
    """Extract tables and text from PDF documents"""
    
    def __init__(self):
        self.ocr = None
        if PADDLE_AVAILABLE:
            try:
                self.ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
            except Exception as e:
                logger.warning(f"Failed to initialize PaddleOCR: {e}")
    
    def extract_tables_from_pdf(self, pdf_path: Union[str, Path]) -> List[pd.DataFrame]:
        """
        Extract all tables from a PDF file
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of DataFrames, one for each table found
        """
        tables = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    page_tables = page.extract_tables()
                    
                    for table_num, table in enumerate(page_tables):
                        if table:
                            # Convert to DataFrame
                            df = pd.DataFrame(table[1:], columns=table[0])
                            df.attrs['source'] = f"Page {page_num}, Table {table_num + 1}"
                            tables.append(df)
                            logger.info(f"Extracted table from page {page_num}")
            
            logger.info(f"Extracted {len(tables)} tables from {pdf_path}")
            return tables
            
        except Exception as e:
            logger.error(f"Error extracting tables from PDF {pdf_path}: {e}")
            return []
    
    def extract_text_from_pdf(self, pdf_path: Union[str, Path]) -> str:
        """
        Extract all text from a PDF file
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text as string
        """
        text = ""
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"
            
            logger.info(f"Extracted {len(text)} characters from {pdf_path}")
            return text
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF {pdf_path}: {e}")
            return ""
    
    def pdf_to_images(self, pdf_path: Union[str, Path]) -> List[Image.Image]:
        """
        Convert PDF pages to images for OCR
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of PIL Images
        """
        images = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    img = page.to_image(resolution=300)
                    images.append(img.original)
            
            logger.info(f"Converted {len(images)} pages to images from {pdf_path}")
            return images
            
        except Exception as e:
            logger.error(f"Error converting PDF to images {pdf_path}: {e}")
            return []
    
    def ocr_image(self, image: Union[Image.Image, str, Path]) -> str:
        """
        Perform OCR on an image
        
        Args:
            image: PIL Image or path to image file
            
        Returns:
            Extracted text
        """
        if not self.ocr:
            logger.warning("OCR not available")
            return ""
        
        try:
            if isinstance(image, (str, Path)):
                image = str(image)
            
            result = self.ocr.ocr(image, cls=True)
            
            # Extract text from result
            text = ""
            if result and result[0]:
                for line in result[0]:
                    if line[1]:
                        text += line[1][0] + " "
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error performing OCR: {e}")
            return ""
    
    def ocr_pdf(self, pdf_path: Union[str, Path]) -> str:
        """
        Perform OCR on all pages of a PDF
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text from all pages
        """
        if not self.ocr:
            logger.warning("OCR not available, falling back to text extraction")
            return self.extract_text_from_pdf(pdf_path)
        
        images = self.pdf_to_images(pdf_path)
        all_text = ""
        
        for i, image in enumerate(images, 1):
            logger.info(f"Performing OCR on page {i}/{len(images)}")
            text = self.ocr_image(image)
            all_text += text + "\n\n"
        
        return all_text


class TableCleaner:
    """Clean and normalize extracted tables"""
    
    @staticmethod
    def clean_table(df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean a DataFrame extracted from PDF/OCR
        
        Args:
            df: Input DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        # Create a copy
        df = df.copy()
        
        # Remove completely empty rows and columns
        df = df.dropna(how='all', axis=0)
        df = df.dropna(how='all', axis=1)
        
        # Strip whitespace from all string columns
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].astype(str).str.strip()
        
        # Replace common OCR errors
        replacements = {
            'O': '0',  # Letter O to zero in numeric contexts
            'l': '1',  # Letter l to one in numeric contexts
            ',': '',   # Remove commas from numbers
        }
        
        # Try to convert numeric-looking columns to numbers
        for col in df.columns:
            # Skip if already numeric
            if pd.api.types.is_numeric_dtype(df[col]):
                continue
            
            # Try conversion
            try:
                df[col] = pd.to_numeric(df[col], errors='ignore')
            except:
                pass
        
        return df
    
    @staticmethod
    def merge_header_rows(df: pd.DataFrame, n_header_rows: int = 2) -> pd.DataFrame:
        """
        Merge multi-row headers into single row
        
        Args:
            df: DataFrame with multi-row headers
            n_header_rows: Number of header rows to merge
            
        Returns:
            DataFrame with merged headers
        """
        if len(df) < n_header_rows:
            return df
        
        # Get header rows
        headers = df.iloc[:n_header_rows].values
        
        # Merge headers
        new_columns = []
        for col_idx in range(headers.shape[1]):
            col_parts = [str(headers[row, col_idx]) for row in range(n_header_rows)]
            # Remove 'nan' and empty strings
            col_parts = [p for p in col_parts if p and p != 'nan']
            new_columns.append(' '.join(col_parts))
        
        # Create new DataFrame
        df_new = df.iloc[n_header_rows:].copy()
        df_new.columns = new_columns
        df_new = df_new.reset_index(drop=True)
        
        return df_new


def download_and_parse_pdf(url: str, save_dir: Optional[Path] = None) -> Dict:
    """
    Download a PDF from URL and extract data
    
    Args:
        url: URL of the PDF file
        save_dir: Optional directory to save the PDF
        
    Returns:
        Dictionary with extracted tables and text
    """
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Save to temp file or specified directory
        if save_dir:
            save_dir.mkdir(parents=True, exist_ok=True)
            filename = save_dir / url.split('/')[-1]
        else:
            import tempfile
            filename = Path(tempfile.mktemp(suffix='.pdf'))
        
        with open(filename, 'wb') as f:
            f.write(response.content)
        
        # Parse the PDF
        parser = PDFParser()
        tables = parser.extract_tables_from_pdf(filename)
        text = parser.extract_text_from_pdf(filename)
        
        return {
            'tables': tables,
            'text': text,
            'filename': str(filename)
        }
        
    except Exception as e:
        logger.error(f"Error downloading and parsing PDF from {url}: {e}")
        return {'tables': [], 'text': '', 'filename': ''}
