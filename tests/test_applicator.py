"""Tests for platform adapters."""
import unittest
from src.applicator.base_adapter import detect_platform


class TestPlatformDetection(unittest.TestCase):
    def test_detect_linkedin(self):
        self.assertEqual(detect_platform("https://www.linkedin.com/jobs/view/123"), "linkedin")

    def test_detect_greenhouse(self):
        self.assertEqual(detect_platform("https://boards.greenhouse.io/company/jobs/123"), "greenhouse")

    def test_detect_lever(self):
        self.assertEqual(detect_platform("https://jobs.lever.co/company/abc-123"), "lever")

    def test_detect_workday(self):
        self.assertEqual(detect_platform("https://company.wd5.myworkday.com/job/123"), "workday")

    def test_detect_indeed(self):
        self.assertEqual(detect_platform("https://www.indeed.com/viewjob?jk=abc"), "indeed")

    def test_detect_naukri(self):
        self.assertEqual(detect_platform("https://www.naukri.com/job-listing-123"), "naukri")

    def test_detect_generic(self):
        self.assertEqual(detect_platform("https://careers.randomcompany.com/apply"), "generic")


class TestAdapterDryRun(unittest.TestCase):
    def test_dry_run_flag(self):
        from src.applicator.generic_adapter import GenericAdapter
        adapter = GenericAdapter(dry_run=True)
        self.assertTrue(adapter.dry_run)

    def test_no_dry_run(self):
        from src.applicator.generic_adapter import GenericAdapter
        adapter = GenericAdapter(dry_run=False)
        self.assertFalse(adapter.dry_run)


if __name__ == "__main__":
    unittest.main()
