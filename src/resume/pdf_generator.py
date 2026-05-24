import logging
import os
import re
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

log = logging.getLogger(__name__)

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "tailored_resumes")


def sanitize_filename(text: str) -> str:
    return re.sub(r'[^\w\s-]', '', text).strip().replace(' ', '_')[:50]


def generate_pdf(resume_data: dict, job: dict) -> str:
    """Generate a tailored PDF resume from structured data.
    Returns the path to the generated PDF."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("resume.html")
    html_content = template.render(**resume_data)

    company = sanitize_filename(job.get("company", "Unknown"))
    title = sanitize_filename(job.get("title", "Job"))
    filename = f"resume_{company}_{title}.pdf"
    output_path = os.path.join(OUTPUT_DIR, filename)

    HTML(string=html_content).write_pdf(output_path)
    log.info(f"Generated tailored PDF: {output_path}")

    return output_path
