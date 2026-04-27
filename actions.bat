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
if "%2"=="patch" (
    bumpver update --patch --allow-dirty
    git add -u
    python devops-scripts\generate_commit.py
    call :confirm_push || ( call :rollback & goto :eof )
    git push --follow-tags
    if "%3"=="--release" (
        for /f %%V in ('bumpver show current-version --no-fetch') do set VERSION=%%V
        gh release create v%VERSION% --title "v%VERSION%" --notes "Automated release"
    )
    goto :eof
)
if "%2"=="minor" (
    bumpver update --minor --allow-dirty
    git add -u
    python devops-scripts\generate_commit.py
    python -m pip install --upgrade build
    python -m build
    call :confirm_push || ( call :rollback & goto :eof )
    git push --follow-tags
    if "%3"=="--release" (
        for /f %%V in ('bumpver show current-version --no-fetch') do set VERSION=%%V
        gh release create v%VERSION% --title "v%VERSION%" --notes "Automated release"
    )
    goto :eof
)
if "%2"=="major" (
    bumpver update --major --allow-dirty
    git add -u
    python devops-scripts\generate_commit.py
    python -m pip install --upgrade build
    python -m build
    call :confirm_push || ( call :rollback & goto :eof )
    git push --follow-tags
    if "%3"=="--release" (
        for /f %%V in ('bumpver show current-version --no-fetch') do set VERSION=%%V
        gh release create v%VERSION% --title "v%VERSION%" --notes "Automated release"
    )
    goto :eof
)

echo Usage: actions update [patch^|minor^|major] [--release]
exit /b 1


REM ── Roll back bump and unstage everything ───────────────────────────────────
git restore --staged .
git restore .
echo  Done. Changes have been rolled back to pre-bump state.
exit /b 0

:rollback
echo  Rolling back version bump...
for /f %%V in ('git describe --tags --abbrev=0') do set VERSION=%%V
git tag -d %VERSION% 2>nul
git reset --hard HEAD~1
echo  Done. Changes have been rolled back to pre-bump state.
exit /b 0


REM ── Confirmation prompt ─────────────────────────────────────────────────────
:confirm_push
echo.
echo  Ready to push. Press ENTER to confirm or ESC to abort...
call :read_key
@REM if "%KEYPRESS%"=="ENTER" (
@REM     echo  Pushing...
@REM     exit /b 0
@REM )
@REM echo  Aborted.
@REM exit /b 1
if "%KEYPRESS%"=="ENTER" (
    echo  Pushing...
    exit /b 0
)
echo  Aborted.
call :rollback
exit /b 1

:read_key
set "KEYPRESS="
for /f "delims=" %%k in ('powershell -noprofile -command "$k = $host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown'); if ($k.VirtualKeyCode -eq 13) { \"ENTER\" } elseif ($k.VirtualKeyCode -eq 27) { \"ESC\" } else { \"OTHER\" }"') do set "KEYPRESS=%%k"
exit /b 0