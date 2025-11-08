import os
import io
from typing import List, Dict, Tuple
import PyPDF2
from PIL import Image
import pytesseract
from pdf2image import convert_from_path


class PDFProcessor:
    """Handle PDF text extraction and image processing"""

    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.total_pages = 0

    def get_total_pages(self) -> int:
        """Get total number of pages in PDF"""
        try:
            with open(self.pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                self.total_pages = len(pdf_reader.pages)
                return self.total_pages
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")

    def extract_text_from_page(self, page_num: int) -> str:
        """Extract text from a specific page (0-indexed)"""
        try:
            with open(self.pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                if page_num >= len(pdf_reader.pages):
                    raise ValueError(f"Page {page_num} does not exist")

                page = pdf_reader.pages[page_num]
                text = page.extract_text()

                return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting text from page {page_num}: {str(e)}")

    def extract_text_from_range(self, start_page: int, end_page: int) -> str:
        """Extract text from a range of pages (0-indexed)"""
        texts = []
        for page_num in range(start_page, end_page + 1):
            text = self.extract_text_from_page(page_num)
            if text:
                texts.append(text)

        return "\n\n".join(texts)

    def is_page_scanned(self, page_num: int, threshold: int = 50) -> bool:
        """Check if a page is scanned (has minimal text)"""
        text = self.extract_text_from_page(page_num)
        return len(text.strip()) < threshold

    def ocr_page(self, page_num: int) -> str:
        """Perform OCR on a specific page"""
        try:
            # Convert PDF page to image
            images = convert_from_path(
                self.pdf_path,
                first_page=page_num + 1,
                last_page=page_num + 1,
                dpi=300
            )

            if not images:
                return ""

            # Perform OCR
            text = pytesseract.image_to_string(images[0], lang='eng+jpn')
            return text.strip()

        except Exception as e:
            raise Exception(f"Error performing OCR on page {page_num}: {str(e)}")

    def extract_page_image(self, page_num: int, max_size: Tuple[int, int] = (1024, 1024)) -> bytes:
        """Extract page as image for vision API (0-indexed)"""
        try:
            # Convert PDF page to image
            images = convert_from_path(
                self.pdf_path,
                first_page=page_num + 1,
                last_page=page_num + 1,
                dpi=150  # Lower DPI for API transmission
            )

            if not images:
                raise Exception("Could not convert page to image")

            # Resize if needed
            image = images[0]
            image.thumbnail(max_size, Image.Resampling.LANCZOS)

            # Convert to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)

            return img_byte_arr.getvalue()

        except Exception as e:
            raise Exception(f"Error extracting image from page {page_num}: {str(e)}")

    def detect_chapters(self) -> List[Dict]:
        """
        Detect chapter boundaries based on text patterns
        Returns list of dicts with chapter info: {number, title, start_page, end_page}
        """
        chapters = []
        current_chapter = None

        for page_num in range(self.total_pages):
            text = self.extract_text_from_page(page_num)

            # Look for chapter patterns (customize based on your PDFs)
            lines = text.split('\n')
            for i, line in enumerate(lines[:5]):  # Check first 5 lines
                line_stripped = line.strip()

                # Pattern matching for chapters
                if self._is_chapter_heading(line_stripped):
                    # Save previous chapter
                    if current_chapter:
                        current_chapter['end_page'] = page_num - 1
                        chapters.append(current_chapter)

                    # Start new chapter
                    chapter_num = len(chapters) + 1
                    current_chapter = {
                        'number': chapter_num,
                        'title': line_stripped,
                        'start_page': page_num,
                        'end_page': None
                    }
                    break

        # Close last chapter
        if current_chapter:
            current_chapter['end_page'] = self.total_pages - 1
            chapters.append(current_chapter)

        # If no chapters detected, treat whole document as one chapter
        if not chapters:
            chapters.append({
                'number': 1,
                'title': 'Full Document',
                'start_page': 0,
                'end_page': self.total_pages - 1
            })

        return chapters

    def _is_chapter_heading(self, line: str) -> bool:
        """Check if a line is likely a chapter heading"""
        import re

        # Common chapter patterns
        patterns = [
            r'^Chapter\s+\d+',
            r'^第[0-9]+章',  # Japanese
            r'^CHAPTER\s+[IVXLCDM]+',  # Roman numerals
            r'^\d+\.\s+[A-Z]',  # "1. Introduction"
            r'^Part\s+\d+',
            r'^Section\s+\d+'
        ]

        for pattern in patterns:
            if re.search(pattern, line, re.IGNORECASE):
                return True

        return False

    def split_into_chunks(self, max_pages_per_chunk: int = 10) -> List[Dict]:
        """
        Split document into manageable chunks for processing
        Returns list of dicts: {start_page, end_page, page_count}
        """
        chunks = []
        total_pages = self.get_total_pages()

        for start in range(0, total_pages, max_pages_per_chunk):
            end = min(start + max_pages_per_chunk - 1, total_pages - 1)
            chunks.append({
                'start_page': start,
                'end_page': end,
                'page_count': end - start + 1
            })

        return chunks
