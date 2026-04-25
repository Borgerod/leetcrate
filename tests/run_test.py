'''
    Dev tool: discovers all problem folders under problems/incomplete and problems/completed,
    then runs the solution file matching the language configured in settings.INI.

    Requires the relevant runtime to be on PATH:
      - python  -> python
      - javascript/js -> node
      - go -> go run
      - java -> javac + java
      - cpp/c++ -> g++ + executable

    Run from the project root:
        python tests/run_test.py
'''

import os
import sys
import subprocess
import configparser
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROBLEMS_DIR = os.path.join(ROOT, "problems")
SETTINGS_PATH = os.path.join(ROOT, "settings.INI")

LANG_EXTENSION: dict[str, str] = {
    "python": ".py",
    "javascript": ".js",
    "js": ".js",
    "go": ".go",
    "java": ".java",
    "cpp": ".cpp",
    "c++": ".cpp",
}


def read_language() -> str:
    config = configparser.ConfigParser()
    try:
        config.read(SETTINGS_PATH, encoding="utf-8-sig")
    except UnicodeDecodeError:
        config.read(SETTINGS_PATH, encoding="utf-16")
    for section in config.sections():
        if config.has_option(section, "language"):
            return config.get(section, "language").strip().lower()
    return "python"


def find_problem_folders() -> list[str]:
    folders: list[str] = []
    for status in ("incomplete", "completed"):
        base = os.path.join(PROBLEMS_DIR, status)
        if not os.path.isdir(base):
            continue
        for entry in sorted(os.listdir(base)):
            full = os.path.join(base, entry)
            if os.path.isdir(full):
                folders.append(full)
    return folders


def find_solution_file(folder: str, extension: str) -> str | None:
    for fname in os.listdir(folder):
        if fname.endswith(extension) and not fname.startswith("__"):
            return os.path.join(folder, fname)
    return None


def run_python(filepath: str) -> int:
    result = subprocess.run([sys.executable, filepath])
    return result.returncode


def run_javascript(filepath: str) -> int:
    result = subprocess.run(["node", filepath])
    return result.returncode


def run_go(filepath: str) -> int:
    result = subprocess.run(["go", "run", filepath])
    return result.returncode


def run_java(filepath: str) -> int:
    folder = os.path.dirname(filepath)
    classname = os.path.splitext(os.path.basename(filepath))[0]
    compile_result = subprocess.run(["javac", filepath], cwd=folder)
    if compile_result.returncode != 0:
        return compile_result.returncode
    run_result = subprocess.run(["java", classname], cwd=folder)
    classfile = os.path.join(folder, classname + ".class")
    if os.path.exists(classfile):
        os.remove(classfile)
    return run_result.returncode


def run_cpp(filepath: str) -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        exe = os.path.join(tmpdir, "solution")
        compile_result = subprocess.run(["g++", "-o", exe, filepath])
        if compile_result.returncode != 0:
            return compile_result.returncode
        run_result = subprocess.run([exe])
        return run_result.returncode


RUNNERS: dict[str, object] = {
    "python": run_python,
    "javascript": run_javascript,
    "js": run_javascript,
    "go": run_go,
    "java": run_java,
    "cpp": run_cpp,
    "c++": run_cpp,
}


def main() -> None:
    language = read_language()
    extension = LANG_EXTENSION.get(language)
    runner = RUNNERS.get(language)

    if not extension or not runner:
        print(f"Unsupported language in settings.INI: '{language}'")
        sys.exit(1)

    print(f"Language: {language}")
    print(f"Extension: {extension}\n")

    folders = find_problem_folders()
    if not folders:
        print("No problem folders found under problems/.")
        sys.exit(0)

    passed = 0
    failed = 0

    for folder in folders:
        name = os.path.basename(folder)
        filepath = find_solution_file(folder, extension)
        if not filepath:
            print(f"  [SKIP]  {name}  (no {extension} file found)")
            continue

        print(f"  [RUN]   {name}")
        returncode = runner(filepath)  # type: ignore[operator]
        if returncode == 0:
            print(f"  [PASS]  {name}\n")
            passed += 1
        else:
            print(f"  [FAIL]  {name}  (exit code {returncode})\n")
            failed += 1

    print(f"\n{'='*40}")
    print(f"Results: {passed} passed, {failed} failed, {len(folders) - passed - failed} skipped")


if __name__ == "__main__":
    main()
