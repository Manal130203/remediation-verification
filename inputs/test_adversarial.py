import unittest
from download import download


class AdversarialSecurityTests(unittest.TestCase):
    def setUp(self):
        self.files = {
            "exports/red/q1.csv": "RED_SECRET",
            "exports/blue/q2.csv": "BLUE_SECRET",
            "exports/red/report final.csv": "SPACE_OK",
        }

    def request(self, path, tenant="red"):
        return download({"tenant": tenant, "path": path}, self.files)

    def assert_denied_without_leak(self, path):
        response = self.request(path)
        self.assertEqual(response["status"], 403, path)
        self.assertEqual(response["body"], "Denied", path)
        self.assertNotIn("RED_SECRET", response["body"])
        self.assertNotIn("BLUE_SECRET", response["body"])

    def test_multiple_parent_segments_are_blocked(self):
        for path in (
            "exports/red/../../blue/q2.csv",
            "exports/red/../../../blue/q2.csv",
            "exports/red/%2e%2e/%2e%2e/blue/q2.csv",
        ):
            with self.subTest(path=path):
                self.assert_denied_without_leak(path)

    def test_encoded_slashes_and_dots_cannot_escape_tenant(self):
        for path in (
            "exports/red/%2e%2e%2fblue/q2.csv",
            "exports%2Fred%2F..%2Fblue%2Fq2.csv",
        ):
            with self.subTest(path=path):
                self.assert_denied_without_leak(path)

    def test_legitimate_encoded_slashes_still_work(self):
        response = self.request("exports%2Fred%2Fq1.csv")
        self.assertEqual(response["status"], 200)
        self.assertEqual(response["body"], "RED_SECRET")

    def test_double_encoding_is_decoded_only_once(self):
        response = self.request("exports/red/%252e%252e/blue/q2.csv")
        self.assertEqual(response["status"], 404)
        self.assertEqual(response["body"], "Missing")
        self.assertNotIn("BLUE_SECRET", response["body"])

    def test_legitimate_dot_segment_is_allowed(self):
        response = self.request("exports/red/./q1.csv")
        self.assertEqual(response["status"], 200)
        self.assertEqual(response["body"], "RED_SECRET")

    def test_legitimate_space_in_filename_is_allowed(self):
        response = self.request("exports/red/report%20final.csv")
        self.assertEqual(response["status"], 200)
        self.assertEqual(response["body"], "SPACE_OK")

    def test_absolute_paths_are_blocked(self):
        for path in ("/exports/red/q1.csv", "C:/exports/red/q1.csv"):
            with self.subTest(path=path):
                self.assert_denied_without_leak(path)

    def test_encoded_backslashes_are_blocked(self):
        self.assert_denied_without_leak("exports%5Cred%5Cq1.csv")

    def test_cross_tenant_access_is_blocked(self):
        self.assert_denied_without_leak("exports/blue/q2.csv")

    def test_sibling_tenant_prefix_is_blocked(self):
        self.files["exports/red-old/secret.txt"] = "SIBLING_SECRET"
        self.assert_denied_without_leak("exports/red-old/secret.txt")

    def test_forbidden_response_never_contains_blue_content(self):
        response = self.request("exports/red/../../blue/q2.csv")
        self.assertEqual(response["status"], 403)
        self.assertNotIn("BLUE_SECRET", response["body"])
        self.assertNotEqual(response["body"], "BLUE_SECRET")


if __name__ == "__main__":
    unittest.main()
