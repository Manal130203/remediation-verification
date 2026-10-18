
import json
import pathlib
import sys

from download import download as fixed_download
from download_original import download as original_download

BASE = pathlib.Path(__file__).parent
FILES = json.loads(
    (BASE / "files.json").read_text(encoding="utf-8")
)

CASES = [
    {
        "name": "Sibling-prefix attack",
        "tenant": "red",
        "path": "exports/red-old/staging.txt",
        "expected": 403,
    },
    {
        "name": "Encoded traversal attack",
        "tenant": "red",
        "path": "exports/red/%2e%2e/blue/q2.csv",
        "expected": 403,
    },
]


def make_request(case):
    return {
        "request_id": case["name"],
        "tenant": case["tenant"],
        "path": case["path"],
    }


def main():
    all_passed = True

    for case in CASES:
        request = make_request(case)
        original = original_download(request, FILES)
        fixed = fixed_download(request, FILES)

        original_vulnerable = original["status"] == 200
        fixed_passed = (
            fixed["status"] == case["expected"]
            and fixed["body"] == "Denied"
        )

        print(f"\n{case['name']}")
        print(f"  Original status: {original['status']}")
        print(f"  Fixed status:    {fixed['status']}")
        print(f"  Fix blocks case: {'PASS' if fixed_passed else 'FAIL'}")
        print(
            "  Original exposes content: "
            f"{'YES' if original_vulnerable else 'NO'}"
        )

        if not fixed_passed or not original_vulnerable:
            all_passed = False

    print(
        "\nOVERALL:",
        "PASS — both known vulnerabilities reproduced and blocked."
        if all_passed
        else "FAIL — inspect the results above.",
    )
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
