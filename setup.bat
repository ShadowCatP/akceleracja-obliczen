@echo off
setlocal

for %%C in (git cmake clang-format nvcc) do (
    where %%C >nul 2>&1
    if errorlevel 1 (
        echo Error: required command not found: %%C
        exit /b 1
    )
)

git config core.hooksPath .githooks
echo Project configured for Windows.
endlocal