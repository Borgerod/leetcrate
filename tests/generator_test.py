'''
    This script runs the leetcode_problem_generator.py script four times, each with a different LeetCode problem slug.
    Purpose: To automate the generation of problem folders and files for a set of LeetCode problems, simulating
    manual terminal runs for each problem. This helps quickly scaffold multiple problems for further development or testing.
'''

import subprocess

slugs = [
    "palindrome-number",
    "search-a-2d-matrix",
    "binary-search",
    "linked-list-cycle",
]

python_path = r"c:/Users/borge/Documents/GitHub/leetcode_organizer_and_generator/.venv/Scripts/python.exe"
script_path = r"c:/Users/borge/Documents/GitHub/leetcode_organizer_and_generator/leetcode_problem_generator.py"

for slug in slugs:
    print(f"\n--- Running for slug: {slug} ---\n")
    result = subprocess.run([
        python_path,
        script_path,
        slug
    ])
    if result.returncode != 0:
        print(f"Error running for slug {slug}, return code: {result.returncode}")
        break
