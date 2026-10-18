# \# ArchiveKit Download Security Remediation

# 

# \## Overview

# 

# This training project investigates and remediates path-validation weaknesses in a fictional tenant-aware download handler.

# 

# The work includes a corrected implementation, regression tests, a comparison against the original vulnerable implementation, and an automated verification script.

# 

# \## Security issues investigated

# 

# \- Sibling-directory prefix bypass.

# \- Percent-encoded path traversal.

# \- Tenant boundary enforcement.

# \- Invalid path rejection and content-disclosure prevention.

# 

# \## Project structure

# 

# ```text

# candidate/

# ├── README.md

# ├── remediation-report.md

# ├── verify.ps1

# ├── inputs/

# │   ├── contract.md

# │   ├── files.json

# │   ├── requests.json

# │   ├── download.py

# │   ├── download\_original.py

# │   ├── download\_before\_test.py

# │   ├── test\_download.py

# │   └── compare\_versions.py

# └── security-tests.txt

# ```

# 

# \## Requirements

# 

# \- Python 3

# \- Windows PowerShell for the provided automation script

# 

# No third-party Python packages are required by the current test workflow.

# 

# \## Run the regression tests

# 

# From the project root:

# 

# ```powershell

# python -m unittest discover -s inputs -p "test\_download.py" -v

# ```

# 

# \## Compare the original and corrected implementations

# 

# ```powershell

# python .\\inputs\\compare\_versions.py

# ```

# 

# The comparison should reproduce two known attacks against the original implementation and verify that the corrected implementation denies both.

# 

# \## Run all checks

# 

# If PowerShell's execution policy permits running the script:

# 

# ```powershell

# .\\verify.ps1

# ```

# 

# For a one-time invocation that does not permanently change the execution policy:

# 

# ```powershell

# powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\\verify.ps1

# ```

# 

# Expected final message:

# 

# ```text

# ALL SECURITY CHECKS PASSED.

# ```

# 

# \## Current verification evidence

# 

# \- 17 regression tests passed.

# \- 2 known attack scenarios reproduced against the original implementation.

# \- Both scenarios denied by the corrected implementation.

# \- Combined verification script completed successfully.

# 

# \## Limitations

# 

# This is a fictional, in-memory training exercise. The results do not establish production security. A real deployment requires integration testing of HTTP parsing, canonical path handling, authorization, and actual storage access.

# 

# See `remediation-report.md` for findings, remediation details, verification results, and residual risks.



