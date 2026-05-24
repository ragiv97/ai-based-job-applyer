"""Tests for job discovery scrapers."""
import unittest
from unittest.mock import patch, MagicMock
from src.discovery.deduplicator import compute_hash, deduplicate_and_store


class TestDeduplicator(unittest.TestCase):
    def test_compute_hash_consistency(self):
        job = {"title": "Python Developer", "company": "Google", "location": "Remote"}
        h1 = compute_hash(job)
        h2 = compute_hash(job)
        self.assertEqual(h1, h2)

    def test_compute_hash_case_insensitive(self):
        job1 = {"title": "Python Developer", "company": "Google", "location": "Remote"}
        job2 = {"title": "python developer", "company": "google", "location": "remote"}
        self.assertEqual(compute_hash(job1), compute_hash(job2))

    def test_different_jobs_different_hashes(self):
        job1 = {"title": "Python Developer", "company": "Google", "location": "Remote"}
        job2 = {"title": "Java Developer", "company": "Google", "location": "Remote"}
        self.assertNotEqual(compute_hash(job1), compute_hash(job2))


class TestJobSpyScraper(unittest.TestCase):
    @patch("src.discovery.jobspy_scraper.scrape_jobs")
    def test_scrape_returns_jobs(self, mock_scrape):
        import pandas as pd
        mock_scrape.return_value = pd.DataFrame([{
            "title": "Python Dev",
            "company_name": "TestCo",
            "location": "Remote",
            "site": "linkedin",
            "job_url": "https://example.com/job/1",
            "description": "A test job",
        }])

        from src.discovery.jobspy_scraper import scrape_jobspy
        jobs = scrape_jobspy(["Python"], ["Remote"], {"linkedin": True})
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["title"], "Python Dev")
        self.assertEqual(jobs[0]["company"], "TestCo")


if __name__ == "__main__":
    unittest.main()
