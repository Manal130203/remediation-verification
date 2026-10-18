
import json
import pathlib
import unittest

from download import download

BASE = pathlib.Path(__file__).parent
FILES = json.loads(
    (BASE / "files.json").read_text(encoding="utf-8")
)


def make_request(tenant, path, request_id="test"):
    return {
        "request_id": request_id,
        "tenant": tenant,
        "path": path,
    }


class DownloadSecurityTests(unittest.TestCase):

    def check_status(self, tenant, path, expected):
        result = download(make_request(tenant, path), FILES)
        self.assertEqual(result["status"], expected, result)

    # 1. Téléchargements légitimes
    def test_red_file(self):
        result = download(
            make_request("red", "exports/red/q1.csv"), FILES
        )
        self.assertEqual(result["status"], 200)
        self.assertEqual(result["body"], "red forecast,120")

    def test_blue_file(self):
        result = download(
            make_request("blue", "exports/blue/q2.csv"), FILES
        )
        self.assertEqual(result["status"], 200)
        self.assertEqual(result["body"], "blue forecast,340")

    def test_encoded_space(self):
        result = download(
            make_request("red", "exports/red/quarter%201.csv"), FILES
        )
        self.assertEqual(result["status"], 200)
        self.assertEqual(
            result["body"], "red encoded-name forecast,125"
        )

    def test_dot_segment_is_normalized(self):
        result = download(
            make_request("red", "exports/red/./q1.csv"), FILES
        )
        self.assertEqual(result["status"], 200)
        self.assertEqual(result["body"], "red forecast,120")

    # 2. Accès interdits
    def test_sibling_prefix_is_denied(self):
        result = download(
            make_request("red", "exports/red-old/staging.txt"), FILES
        )
        self.assertEqual(result["status"], 403)
        self.assertEqual(result["body"], "Denied")

    def test_private_file_is_denied(self):
        self.check_status("red", "private/operator.txt", 403)

    def test_other_tenant_is_denied(self):
        result = download(
            make_request("red", "exports/blue/q2.csv"), FILES
        )
        self.assertEqual(result["status"], 403)
        self.assertNotEqual(result["body"], FILES["exports/blue/q2.csv"])

    def test_encoded_traversal_is_denied(self):
        self.check_status(
            "red", "exports/red/%2e%2e/blue/q2.csv", 403
        )

    # 3. Chemins invalides
    def test_absolute_path_is_denied(self):
        self.check_status("red", "/private/operator.txt", 403)

    def test_backslash_is_denied(self):
        self.check_status("red", r"exports/red\q1.csv", 403)

    def test_encoded_backslash_is_denied(self):
        self.check_status("red", "exports/red%5cq1.csv", 403)

    def test_unknown_tenant_is_denied(self):
        self.check_status("green", "exports/green/q1.csv", 403)

    def test_double_encoded_traversal_is_not_decoded_twice(self):
        result = download(
            make_request(
                "red",
                "exports/red/%252e%252e/blue/q2.csv",
            ),
            FILES,
        )
        self.assertEqual(result["status"], 404)
        self.assertEqual(result["body"], "Missing")
        self.assertNotEqual(result["body"], FILES["exports/blue/q2.csv"])

    # 4. Fichier absent dans le répertoire autorisé
    def test_missing_file_returns_404(self):
        result = download(
            make_request("red", "exports/red/missing.csv"), FILES
        )
        self.assertEqual(result["status"], 404)
        self.assertEqual(result["body"], "Missing")

    def test_denied_response_does_not_leak_file_content(self):
        secret = FILES["exports/red-old/staging.txt"]
        result = download(
            make_request("red", "exports/red-old/staging.txt"),
            FILES,
        )
        self.assertEqual(result["status"], 403)
        self.assertNotEqual(result["body"], secret)
        self.assertNotIn(secret, result["body"])
        self.assertNotIn("DEMO_NONFUNCTIONAL", result["body"])

    def test_encoded_slash_cannot_bypass_tenant_boundary(self):
        result = download(
            make_request("red", "exports%2fblue%2fq2.csv"),
            FILES,
        )
        self.assertEqual(result["status"], 403, result)
        self.assertEqual(result["body"], "Denied")
        self.assertNotEqual(result["body"], FILES["exports/blue/q2.csv"])

    def test_multiple_parent_segments_are_denied(self):
        result = download(
            make_request(
                "red",
                "exports/red/../../private/operator.txt",
            ),
            FILES,
        )
        self.assertEqual(result["status"], 403, result)
        self.assertEqual(result["body"], "Denied")


if __name__ == "__main__":
    unittest.main(verbosity=2)
