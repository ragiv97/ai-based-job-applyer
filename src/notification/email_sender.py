import logging
import os
import smtplib
from datetime import datetime
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

log = logging.getLogger(__name__)


def send_application_email(job: dict, resume_pdf_path: str):
    """Send notification email after successful application with tailored PDF attached."""
    gmail_email = os.getenv("GMAIL_EMAIL")
    gmail_password = os.getenv("GMAIL_APP_PASSWORD")

    if not gmail_email or not gmail_password:
        log.warning("Gmail credentials not configured, skipping email notification")
        return

    subject = f"Applied — {job['title']} at {job['company']}"

    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
    <h2 style="color: #2e7d32;">Application Submitted</h2>
    <table style="border-collapse: collapse; width: 100%;">
        <tr><td style="padding: 8px; font-weight: bold;">Company</td><td style="padding: 8px;">{job['company']}</td></tr>
        <tr><td style="padding: 8px; font-weight: bold;">Job Title</td><td style="padding: 8px;">{job['title']}</td></tr>
        <tr><td style="padding: 8px; font-weight: bold;">Platform</td><td style="padding: 8px;">{job.get('platform', 'N/A')}</td></tr>
        <tr><td style="padding: 8px; font-weight: bold;">Applied at</td><td style="padding: 8px;">{datetime.now().strftime('%B %d, %Y at %I:%M %p')}</td></tr>
        <tr><td style="padding: 8px; font-weight: bold;">Job URL</td><td style="padding: 8px;"><a href="{job.get('job_url', '#')}">{job.get('job_url', 'N/A')}</a></td></tr>
        <tr><td style="padding: 8px; font-weight: bold;">Relevance Score</td><td style="padding: 8px;">{job.get('relevance_score', 'N/A')}/10</td></tr>
    </table>
    <p style="margin-top: 16px; color: #666;">Tailored resume attached.</p>
    </body>
    </html>
    """

    msg = MIMEMultipart()
    msg["From"] = gmail_email
    msg["To"] = gmail_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))

    # Attach tailored resume PDF
    if resume_pdf_path and os.path.exists(resume_pdf_path):
        with open(resume_pdf_path, "rb") as f:
            attachment = MIMEApplication(f.read(), _subtype="pdf")
            attachment.add_header(
                "Content-Disposition", "attachment",
                filename=os.path.basename(resume_pdf_path),
            )
            msg.attach(attachment)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_email, gmail_password)
            server.sendmail(gmail_email, gmail_email, msg.as_string())
        log.info(f"Email sent for '{job['title']}' at {job['company']}")
    except Exception as e:
        log.error(f"Failed to send email: {e}")


def send_daily_summary(applied: int, failed: int, skipped: int, total_discovered: int):
    """Send end-of-day summary email."""
    gmail_email = os.getenv("GMAIL_EMAIL")
    gmail_password = os.getenv("GMAIL_APP_PASSWORD")

    if not gmail_email or not gmail_password:
        return

    subject = f"Daily Job Bot Summary — {datetime.now().strftime('%B %d, %Y')}"

    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
    <h2>Daily Job Bot Summary</h2>
    <table style="border-collapse: collapse;">
        <tr><td style="padding: 8px; font-weight: bold;">New Jobs Discovered</td><td style="padding: 8px;">{total_discovered}</td></tr>
        <tr><td style="padding: 8px; font-weight: bold; color: #2e7d32;">Applications Submitted</td><td style="padding: 8px;">{applied}</td></tr>
        <tr><td style="padding: 8px; font-weight: bold; color: #c62828;">Failed</td><td style="padding: 8px;">{failed}</td></tr>
        <tr><td style="padding: 8px; font-weight: bold; color: #f57f17;">Skipped (low score)</td><td style="padding: 8px;">{skipped}</td></tr>
    </table>
    <p style="margin-top: 16px; color: #666;">Run completed at {datetime.now().strftime('%I:%M %p')}</p>
    </body>
    </html>
    """

    msg = MIMEMultipart()
    msg["From"] = gmail_email
    msg["To"] = gmail_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_email, gmail_password)
            server.sendmail(gmail_email, gmail_email, msg.as_string())
        log.info("Daily summary email sent")
    except Exception as e:
        log.error(f"Failed to send daily summary: {e}")
