'''
    Runs leetcrate generate for each slug in the list below.
    Purpose: Quickly scaffold multiple problems for dev/testing without manual terminal runs.
    Uses the installed leetcrate CLI via the current Python environment.
'''

import sys
import subprocess

slugs = [
    "palindrome-number",
    "search-a-2d-matrix",
    "binary-search",
    "linked-list-cycle",
]

for slug in slugs:
    print(f"\n--- Running for slug: {slug} ---\n")
    result = subprocess.run(
        [sys.executable, "-m", "leetcrate", "generate", slug],
        cwd="..",
    )
    if result.returncode != 0:
        print(f"Error running for slug {slug}, return code: {result.returncode}")
        break
