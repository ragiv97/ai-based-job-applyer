import sqlite3
from datetime import datetime
from typing import Optional
from .models import get_connection


class JobRepository:
    def insert_job(self, job: dict) -> bool:
        conn = get_connection()
        try:
            conn.execute(
                """INSERT OR IGNORE INTO jobs (hash, title, company, location, platform, job_url, description)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (job["hash"], job["title"], job["company"],
                 job.get("location"), job.get("platform"),
                 job.get("job_url"), job.get("description")),
            )
            conn.commit()
            return conn.total_changes > 0
        finally:
            conn.close()

    def job_exists(self, job_hash: str) -> bool:
        conn = get_connection()
        try:
            row = conn.execute("SELECT 1 FROM jobs WHERE hash = ?", (job_hash,)).fetchone()
            return row is not None
        finally:
            conn.close()

    def get_jobs_by_status(self, status: str, limit: int = 100) -> list[dict]:
        conn = get_connection()
        try:
            rows = conn.execute(
                "SELECT * FROM jobs WHERE status = ? ORDER BY created_at DESC LIMIT ?",
                (status, limit),
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def get_unscored_jobs(self, limit: int = 5000) -> list[dict]:
        conn = get_connection()
        try:
            rows = conn.execute(
                "SELECT * FROM jobs WHERE relevance_score IS NULL AND status = 'DISCOVERED' LIMIT ?",
                (limit,),
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def get_ready_to_apply(self, min_score: int, limit: int = 20) -> list[dict]:
        conn = get_connection()
        try:
            rows = conn.execute(
                """SELECT * FROM jobs
                   WHERE relevance_score >= ? AND status = 'DISCOVERED'
                   ORDER BY relevance_score DESC LIMIT ?""",
                (min_score, limit),
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def update_score(self, job_id: int, score: int):
        conn = get_connection()
        try:
            new_status = "DISCOVERED" if score >= 1 else "SKIPPED"
            conn.execute(
                "UPDATE jobs SET relevance_score = ?, status = ? WHERE id = ?",
                (score, new_status, job_id),
            )
            conn.commit()
        finally:
            conn.close()

    def update_status(self, job_id: int, status: str, **kwargs):
        conn = get_connection()
        try:
            sets = ["status = ?"]
            vals = [status]
            if "tailored_resume_path" in kwargs:
                sets.append("tailored_resume_path = ?")
                vals.append(kwargs["tailored_resume_path"])
            if status == "APPLIED":
                sets.append("applied_at = ?")
                vals.append(datetime.now().isoformat())
            vals.append(job_id)
            conn.execute(f"UPDATE jobs SET {', '.join(sets)} WHERE id = ?", vals)
            conn.commit()
        finally:
            conn.close()

    def get_daily_applied_count(self) -> int:
        conn = get_connection()
        try:
            row = conn.execute(
                "SELECT COUNT(*) as cnt FROM jobs WHERE status = 'APPLIED' AND DATE(applied_at) = DATE('now')"
            ).fetchone()
            return row["cnt"]
        finally:
            conn.close()

    def get_stats(self) -> dict:
        conn = get_connection()
        try:
            rows = conn.execute(
                "SELECT status, COUNT(*) as cnt FROM jobs GROUP BY status"
            ).fetchall()
            return {r["status"]: r["cnt"] for r in rows}
        finally:
            conn.close()
