# usage: python scripts/generate_commit_and_push.py
import subprocess
import toml

# Read version from pyproject.toml
with open("pyproject.toml") as f:
    pyproject = toml.load(f)
version = pyproject["project"]["version"]

# Get staged diff summary
diff = subprocess.check_output(["git", "diff", "--cached", "--name-status"], text=True)
files = [line.split('\t')[1] for line in diff.strip().split('\n') if line]
short_desc = "feat(core): update project files"
patch_notes = "\n".join(f"* Update {file}" for file in files)

commit_msg = f"""v{version}
feat(core): update project files

Patch Notes:
{patch_notes}
"""

# Commit and push
subprocess.run(["git", "commit", "-m", commit_msg])
# subprocess.run(["git", "push"])

