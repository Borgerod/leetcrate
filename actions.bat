@echo off
setlocal

REM Activate Python venv
call .venv\Scripts\activate

REM Default: show usage if wrong/no args
if "%1"=="" (
    echo Usage: actions update [patch^|minor^|major] [--release]
    exit /b 1
)

REM Version bump & build logic
if "%1"=="update" (
    if "%2"=="patch" (
        bumpver update --patch
        git add -u
        python devops-scripts\generate_commit.py
        git push --follow-tags
        goto :eof
    )
    if "%2"=="minor" (
        bumpver update --minor
        git add -u
        python devops-scripts\generate_commit.py
        python -m pip install --upgrade build
        python -m build
        git push --follow-tags
        if "%3"=="--release" (
            for /f %%V in ('bumpver show current-version') do set VERSION=%%V
            gh release create v%VERSION% --title "v%VERSION%" --notes "Automated release"
        )
        goto :eof
    )
    if "%2"=="major" (
        bumpver update --major
        git add -u
        python devops-scripts\generate_commit.py
        python -m pip install --upgrade build
        python -m build
        git push --follow-tags
        if "%3"=="--release" (
            for /f %%V in ('bumpver show current-version') do set VERSION=%%V
            gh release create v%VERSION% --title "v%VERSION%" --notes "Automated release"
        )
        goto :eof
    )
)

echo Usage: actions update [patch|minor|major] [--release]
exit /b 1