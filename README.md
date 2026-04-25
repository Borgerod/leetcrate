# leetcrate

A CLI tool that fetches LeetCode problems via the GraphQL API and generates
language-specific boilerplate solution files with runnable test harnesses.

---

## Table of Contents

- [leetcrate](#leetcrate)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
    - [From source (editable install)](#from-source-editable-install)
    - [Verify](#verify)
  - [Configuration](#configuration)
  - [Usage](#usage)
    - [`init`](#init)
    - [`generate`](#generate)
    - [`update`](#update)
  - [Folder Structure](#folder-structure)
  - [Generated File Format](#generated-file-format)
  - [Language Notes](#language-notes)
  - [Dev Tools](#dev-tools)
    - [`tests/generator_test.py`](#testsgenerator_testpy)
    - [`tests/run_test.py`](#testsrun_testpy)
  - [Troubleshooting](#troubleshooting)
  - [TODO:](#todo)

---

## Overview

- Fetch problem metadata via LeetCode's GraphQL API
- Generate boilerplate solutions in five languages: Python, JavaScript, Go, Java, and C++
- Populate runnable test harnesses for every supported language
- Organize output inside `problems/` under `completed/` and `incomplete/`
- Optional workspace folders for contests, courses, and interview prep

---

## Prerequisites

- **Python 3.10+** on your `PATH`
- **requests** package (installed automatically with the package)

---

## Installation

### From source (editable install)

```powershell
git clone https://github.com/Borgerod/leetcrate.git
cd leetcrate
pip install -e .
```

### Verify

```powershell
leetcrate --version
```

---

## Configuration

Run `leetcrate init` in your workspace directory to create a `settings.INI`:

```ini
[LeetCode Problem Generator]
language = python

[Framework]
contests = false
courses  = false
interview = false
```

**Accepted language values** (case-insensitive):

| Value               | File extension |
| ------------------- | -------------- |
| `python`            | `.py`          |
| `javascript` / `js` | `.js`          |
| `go`                | `.go`          |
| `java`              | `.java`        |
| `c++` / `cpp`       | `.cpp`         |

The file is re-read on every run — no restart needed after a language change.

---

## Usage

### `init`

First-time setup. Creates the workspace framework and `settings.INI`.

```powershell
leetcrate init
```

You will be prompted to choose a full framework or a minimal install, and
optionally enable the `contests`, `courses`, and `interview` folders.

---

### `generate`

Fetch a problem and write template files.

```powershell
leetcrate generate two-sum
# or pass the full URL:
leetcrate generate https://leetcode.com/problems/two-sum/
# omit the slug to be prompted interactively:
leetcrate generate
```

What happens:

1. Fetches problem data (title, difficulty, description, tags)
2. Downloads the official code snippet for your configured language
3. Parses function signatures and example test cases
4. Creates `problems/incomplete/<id>_<Title>/`
5. Writes a language-specific file with a stub solution and a working test harness

If the folder already exists the script updates it without overwriting any
solution you have already written. Move a finished solution into
`problems/completed/` to track progress.

---

### `update`

Add any optional folders that are enabled in `settings.INI` but not yet
present on disk.

```powershell
leetcrate update
```

---

## Folder Structure

Running `leetcrate init` with all optional folders enabled creates:

```
./_your_workspace_/
    ├── settings.INI
    ├── problems/
    │   ├── completed/
    │   └── incomplete/
[OPTIONAL]
    ├── contests/
    │   ├── bi_weekly/
    │   └── weekly/
    ├── courses/
    └── interview/
        ├── mock_assessment/
        └── online_interview/
            └── [Name of workplace]/
```

A generated problem folder looks like:

```
problems/
    incomplete/
        1_Two_Sum/
            description.txt      # Cleaned plain-text problem statement
            two_sum.py           # Boilerplate stub + runnable test harness
```

---

## Generated File Format

Each solution file contains:

- The official function/class stub from LeetCode
- A test harness that exercises every example case from the problem statement
- A git commit message template at the bottom (for copy-paste convenience)

---

## Language Notes

| Language       | Test runner style                                                           |
| -------------- | --------------------------------------------------------------------------- |
| **Python**     | `if __name__ == "__main__"` with a `for` loop over cases                    |
| **JavaScript** | `console.log` for each case                                                 |
| **Go**         | `main()` with typed slice literals and fmt.Println                          |
| **Java**       | `Object[][]` cases, casted to parameter types, printed with Arrays.toString |
| **C++**        | `std::vector<std::pair<...>>` cases, printed via helper loops               |

Linked-list problems automatically inject the `ListNode` class and a
`build_linked_list` helper into the generated file.

---

## Dev Tools

Both scripts live in `tests/` and are intended for local development only.

### `tests/generator_test.py`

Bulk-generates a hardcoded list of problems using `leetcrate generate`.
Edit the `slugs` list inside the file to change which problems are scaffolded.

```powershell
python tests/generator_test.py
```

### `tests/run_test.py`

Discovers every problem folder under `problems/` and runs the solution file
that matches the language in `settings.INI`.

```powershell
python tests/run_test.py
```

Runtime requirements per language:

| Language   | Required on PATH |
| ---------- | ---------------- |
| python     | `python`         |
| javascript | `node`           |
| go         | `go`             |
| java       | `javac` + `java` |
| cpp / c++  | `g++`            |

---

## Troubleshooting

| Issue                                     | Fix                                                                            |
| ----------------------------------------- | ------------------------------------------------------------------------------ |
| `No settings.INI found`                   | Run `leetcrate init` first                                                     |
| `Warning: Could not read settings.INI`    | Ensure the file is UTF-8 encoded and contains a valid `language = value` line  |
| Locked problem fetch fails                | Log in to LeetCode in a browser first, or avoid locked problems                |
| Wrong types in test harness               | Check your `language` value in `settings.INI` matches the file you want to run |
| Need to re-generate after language change | Delete the folder and run `leetcrate generate <slug>` again                    |

## TODO:

- [x] Make generator for extra testcases
  - [x] Fix broken testcase generator
- [x] Make generator for git push description.
- [x] crate tests/run_test.py - will run the 4 generates files (according to set language in settings.ini) (NOTE: this is a dev tool).
  - [ ] install c++, java, javascript and go in /.venv, so dev can run the codes locally and not rely on online compilers while building.
- [x] crate tests/generator_test.py - will generates cases for set language (settings.ini) for the leetcode projects set in generator_test (NOTE: this is a dev tool).
- [x] Update v0.2.0 - descr: <br>
      _add clause for handling nodes, add Adjusted test runner(iterates over (vals, pos) pairs for linked list problems), dynamic type notations, add dynamic comments._
  - [x] Update script: Python
  - [x] Update script: C++
  - [x] Update script: Java
  - [x] Update script: JavaScript
  - [x] Update script: Go
- [ ] Add docs to python components
- [x] Turn project into package
  - [x] Add package directory structure (src/ if needed)
  - [x] Ensure all modules have **init**.py
  - [x] Update pyproject.toml with metadata
  - [x] Specify dependencies in pyproject.toml
  - [x] Add classifiers and license info
  - [x] Add README.md with usage
  - [x] Add LICENSE file
  - [ ] Add MANIFEST.in if needed
  - [ ] Test local install (pip install -e .)
  - [ ] Verify import/usage from clean env

  [_OPTIONAL_]
  - [ ] (Optional) Add setup.cfg/setup.py
  - [x] (Optional) Add tests/ directory
  - [ ] (Optional) Set up CI
  - [ ] (Optional) Publish to PyPI
