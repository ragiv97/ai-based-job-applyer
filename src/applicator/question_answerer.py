import json
import logging
import subprocess

log = logging.getLogger(__name__)


def answer_custom_question(question: str, job_info: dict, profile: dict) -> str:
    """Use Claude Code CLI to answer custom application questions."""
    prompt = f"""Answer this job application question professionally and concisely.

QUESTION: {question}
JOB: {job_info.get('title', '')} at {job_info.get('company', '')}
CANDIDATE PROFILE: {json.dumps(profile)}

Rules:
- Be honest, never fabricate experience
- Keep answers under 150 words unless asked for more
- Match the tone to the company culture if identifiable
- Return ONLY the answer text, nothing else"""

    try:
        result = subprocess.run(
            ["claude", "-p", prompt],
            capture_output=True,
            text=True,
            timeout=30,
        )
        answer = result.stdout.strip()
        log.info(f"Answered question: '{question[:50]}...' → {len(answer)} chars")
        return answer
    except Exception as e:
        log.error(f"Failed to answer question '{question[:50]}': {e}")
        return ""
