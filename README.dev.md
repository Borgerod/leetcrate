# Tools

---

## Table of Contents

- [Tools](#tools)
  - [Table of Contents](#table-of-contents)
  - [Devops commands - push, build, release.](#devops-commands---push-build-release)
    - [commands:](#commands)
    - [patch](#patch)
    - [minor](#minor)
    - [major](#major)
    - [build + release without pushing](#build--release-without-pushing)

---

## Devops commands - push, build, release.

_after staging changes_
updating patch will only push.
minor - will also build and release.
major - will also build and release.

### commands:

```cmd
action update patch
action update minor --release
action update major --release
```

### patch

    ```cmd
    .venv\Scripts\activate
    bumpver update --patch
    python scripts/generate_commit.py
    git push --follow-tags
    ```

### minor

    ```cmd
    .venv\Scripts\activate
    bumpver update --minor
    python scripts/generate_commit.py
    python -m pip install --upgrade build
    python -m build
    git push --follow-tags
    gh release create v$(bumpver show current-version) --title "v$(bumpver show current-version)" --notes "Automated release"
    ```

### major

    ```cmd
    .venv\Scripts\activate
    bumpver update --major
    python scripts/generate_commit.py
    python -m pip install --upgrade build
    python -m build
    git push --follow-tags
    gh release create v$(bumpver show current-version) --title "v$(bumpver show current-version)" --notes "Automated release"
    ```

### build + release without pushing

    ```cmd
    python -m pip install --upgrade build
    python -m build
    git push --follow-tags
    gh release create v1.2.0 --title "v1.2.0" --notes "Automated release"
    ```
