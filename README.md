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
    - [From PyPI](#from-pypi)
  - [Configuration](#configuration)
  - [Usage](#usage)
    - [`init`](#init)
    - [`generate`](#generate)
    - [`update`](#update)
    - [commands overview / all commands](#commands-overview--all-commands)
  - [Folder Structure](#folder-structure)
  - [Generated File Format](#generated-file-format)
  - [Language Notes](#language-notes)
  - [Dev Tools](#dev-tools)
    - [`tests/generator_test.py`](#testsgenerator_testpy)
    - [`tests/run_test.py`](#testsrun_testpy)
  - [Troubleshooting](#troubleshooting)
  - [TODO:](#todo)
    - [_\[ plans for 1.0 -\> 2.0 \]_](#-plans-for-10---20-)

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

### From PyPI

```powershell
pip install leetcrate
```

<!-- ### From source (editable install)

```powershell
git clone https://github.com/Borgerod/leetcrate.git
cd leetcrate
pip install -e .
``` -->
<!--
### Verify

```powershell
leetcrate --version
``` -->

---

## Configuration

Run `leetcrate init` in your workspace directory to create a `settings.INI`:

```ini
[LeetCode Problem Generator]
; Pick from [python, cpp, java, javascript, go]
language = python

[Framework]
; set these to true and run 'leetcrate update' to add other folders to your repo after the fact.
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

You will be prompted to choose a full framework or a minimal install;
<br> &emsp; 1. minimal install &nbsp; -> For when you already have a file system and only want to use the package.
<br> &emsp; 2. framework &emsp;&emsp; -> For when you are starting fresh, installs the package and creates framework;
<br> &emsp; &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&nbsp;&nbsp; optionally enable the `contests`, `courses`, and `interview` folders.

<!-- You will be prompted to choose a full framework or a minimal install, and
optionally enable the `contests`, `courses`, and `interview` folders. -->

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

### commands overview / all commands

<!-- ```powershell
# tool commands
leetcrate init                             # framework setup
leetcrate update                           # updates framework based on setttings.ini
leetcrate generate _some_leetcode_slug_    # creates template code in ./problems/incomplete

# Basic commands
leetcrate --version                        # verify version
leetcrate --update                         # updates leetcrate version
leetcrate --help                           # get tool commands
``` -->

```powershell
# tool commands
leetcrate init
leetcrate update
leetcrate generate _some_leetcode_slug_

# Basic commands
leetcrate --version
leetcrate --update
leetcrate --help
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

| Issue                                     | Fix                                                                                     |
| ----------------------------------------- | --------------------------------------------------------------------------------------- |
| `No settings.INI found`                   | Run `leetcrate init` first                                                              |
| `Warning: Could not read settings.INI`    | Ensure the file is UTF-8 encoded and contains a valid `language = value` line           |
| Locked problem fetch fails                | Log in to LeetCode in a browser first, or avoid locked problems                         |
| Wrong types in test harness               | Check your `language` value in `settings.INI` matches the file you want to run          |
| Need to re-generate after language change | Delete the folder and run `leetcrate generate <slug>` again                             |
| `leetcrate` not recognized after install  | Run cmd as Administrator, then `pip uninstall leetcrate -y` and `pip install leetcrate` |

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
- [x] Add docs to python components
- [x] Turn project into package
  - [x] Add package directory structure (src/ if needed)
  - [x] Ensure all modules have **init**.py
  - [x] Update pyproject.toml with metadata
  - [x] Specify dependencies in pyproject.toml
  - [x] Add classifiers and license info
  - [x] Add README.md with usage
  - [x] Add LICENSE file
  - [ ] Add MANIFEST.in if needed
  - [x] Test local install (pip install -e .)
  - [x] Verify import/usage from clean env

  [_OPTIONAL_]
  - [ ] (Optional) Add setup.cfg/setup.py
  - [x] (Optional) Add tests/ directory
  - [ ] (Optional) Set up CI
  - [x] (Optional) Publish to PyPI

### _[ plans for 1.0 -> 2.0 ]_

- [ ] Add Migration tool - _for when users already have a repo for thier leetcode solutions and want to migrate them into the dataframe_
  - [ ] add command; "leetcrate migrate _Path_To_Solutions_"
  - [ ] default - assuming the user's _Path_To_Solutions_ is a regular folder; <details>
        <summary>Section Title</summary>

                Content inside the expandable section goes here.
                ```
                ./_Path_To_Solutions_/
                    ├── _leetcode_solution_1_
                    ├── _leetcode_solution_2_
                    ├── _leetcode_solution_3_
                    .
                    .
                    .
                    └──_leetcode_solution_n_
                ```
        </details>

  - [ ] variant - For when the user's repo has a more complex file structure - add a parser that takes a _structure_description_ as a param, then let the user describe the structure somewhere. <details>
        <summary>Section Title</summary>

                Content inside the expandable section goes here.
                ```
                ./_Path_To_Solutions_/
                    ├── _leetcode_solution_1_
                    ├── _leetcode_solution_2_
                    ├── _leetcode_solution_3_
                    .
                    .
                    .
                    └──_leetcode_solution_n_
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
        </details>

  - [ ] options:
  1.  (safe but easy)Parse + iterates _solution_files_ then; generates templates based on them. <details>
      <summary> read more.. </summary> 1. This will require either that, the user _solution_files_ provides something uniqe and recognizable.
      <br> &emsp;&emsp; a. the _solution_file_ has the slug in its name,
      <br> &emsp;&emsp; b. the proper name function name in side of it i.e.: "... def twoSum...", ,
      <br> &emsp;&emsp; c. the user simply adds a list of solutions, but that sort of ruins the purpose.<br>
      2. The migration tool will then essentially run "leetcrate generate _slug_" for each _solution_file_.<br>
      3. Then the user will have to manually replace the templates with their own code,
         which is safer but more laborous for the user.<br><br>

      </details>

  2.  (less safe but proper) Parse + iterates _solution_files_ then; automatically integrate content to template. <details>
      <summary> read more.. </summary>
      will generate template from it (require recognizable naming),
      <br>
      then make a copy _solution_files_ (for saftey),
      <br>
      then insert its content into the generated tempalte.
      <br><br>
      ! might need a rollback failsafe since this could be destructive depending on how i make it, or issue a warning to make sure the user is backed up before continuing.
      </details>

  <!-- - [ ] add DevOps tools: -->
  <!-- - [ ] add CI/CD tools: -->

- [ ] Add VCS tools:
  - [ ] Add command - marking _solution_file_ as solved -> move to ./completed
  - [ ] Add command - pushing completed file to repo w/ generated commit message
  - [ ] Add command - pushing incomplete file to repo w/ generated commit message
- [ ] Add more languages
  - [ ] [1.1]
    - [ ] Typescript
    - [ ] C#
    - [ ] C \*_gulp_\*
    - [ ] Rust \*_gulp_\*
  - [ ] [1.2]
    - [ ] Kotlin
    - [ ] Swift
    - [ ] Dart
    - [ ] PHP
  - [ ] [1.3]
    - [ ] Ruby
    - [ ] Racket
    - [ ] Scala
    - [ ] Erlang
    - [ ] Elixir
- [ ] Make compatible for other package-types; npm, NuGet, Apache Maven, etc [ _MAYBE_ ]
