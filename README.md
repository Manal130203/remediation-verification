# ArchiveKit Download Security Remediation

## Overview

This training project investigates and remediates path-validation weaknesses in a fictional tenant-aware download handler.

The work includes a corrected implementation, regression tests, a comparison against the original vulnerable implementation, and an automated verification script.

## Security issues investigated

- Sibling-directory prefix bypass.
- Percent-encoded path traversal.
- Tenant boundary enforcement.
- Invalid path rejection and content-disclosure prevention.

## Project structure

```text
candidate/
├── README.md
├── remediation-report.md
├── verify.ps1
├── inputs/
│   ├── contract.md
│   ├── files.json
│   ├── requests.json
│   ├── download.py
│   ├── download_original.py
│   ├── download_before_test.py
│   ├── test_download.py
│   ├── test_adversarial.py
│   └── compare_versions.py
└── security-tests.txt
```

## Requirements

- Python 3
- PowerShell

No third-party Python packages are required for the regression and adversarial tests. Ruff and Bandit may be used as additional code-quality and security checks in the verification workflow.

## Run the regression tests

From the project root:

```powershell
python -m unittest discover -s inputs -p "test_download.py" -v
```

## Run the adversarial security tests

```powershell
python -m unittest discover -s inputs -p "test_adversarial.py" -v
```

## Compare the original and corrected implementations

```powershell
python .\inputs\compare_versions.py
```

The comparison reproduces two known attacks against the original implementation and verifies that the corrected implementation denies both.

## Run all checks

```powershell
.\verify.ps1
```

If PowerShell blocks script execution, you can invoke it for this run without permanently changing the execution policy:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\verify.ps1
```

Expected final message:

```text
ALL SECURITY CHECKS PASSED.
```

## Current verification evidence

The latest recorded verification reported:

- 17 regression tests passed.
- 11 adversarial security tests passed.
- Two known attack scenarios reproduced against the original implementation.
- Both scenarios denied by the corrected implementation.
- Bandit reported no issues in the scanned code.
- The combined verification completed successfully.

## Limitations

This is a fictional, in-memory training exercise. The results do not establish production security. A real deployment requires integration testing of HTTP parsing, canonical path handling, authorization, and actual storage access.

See `remediation-report.md` for findings, remediation details, verification results, and residual risks.