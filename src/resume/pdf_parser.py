import logging
import pymupdf4llm

log = logging.getLogger(__name__)


def parse_resume_pdf(pdf_path: str) -> str:
    """Parse a PDF resume into Markdown text using PyMuPDF4LLM."""
    try:
        md_text = pymupdf4llm.to_markdown(pdf_path)
        log.info(f"Parsed resume: {len(md_text)} chars from {pdf_path}")
        return md_text
    except Exception as e:
        log.error(f"Failed to parse PDF {pdf_path}: {e}")
        raise
