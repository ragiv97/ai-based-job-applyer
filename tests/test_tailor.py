"""Tests for resume tailoring."""
import json
import unittest
from unittest.mock import patch, MagicMock


class TestClaudeTailor(unittest.TestCase):
    @patch("subprocess.run")
    def test_tailor_resume_returns_valid_json(self, mock_run):
        mock_result = MagicMock()
        mock_result.stdout = json.dumps({
            "name": "Test User",
            "contact": {"email": "test@test.com", "phone": "123", "linkedin": ""},
            "summary": "Experienced developer",
            "experience": [{"title": "Dev", "company": "Co", "duration": "2y", "bullets": ["Did stuff"]}],
            "education": [{"degree": "BS CS", "institution": "MIT", "year": "2020"}],
            "skills": ["Python", "Django"],
            "projects": [],
        })
        mock_run.return_value = mock_result

        from src.resume.claude_tailor import tailor_resume
        result = tailor_resume("# Resume\nJohn Doe", {
            "title": "Python Dev",
            "company": "TestCo",
            "description": "We need a Python developer",
        })

        self.assertEqual(result["name"], "Test User")
        self.assertIn("Python", result["skills"])


class TestPdfGenerator(unittest.TestCase):
    def test_sanitize_filename(self):
        from src.resume.pdf_generator import sanitize_filename
        self.assertEqual(sanitize_filename("Google Inc."), "Google_Inc")
        self.assertEqual(sanitize_filename("Sr. Python Dev!"), "Sr_Python_Dev")


if __name__ == "__main__":
    unittest.main()
