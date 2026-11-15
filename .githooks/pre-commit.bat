@echo off
setlocal EnableExtensions

echo pre-commit checks...
echo formatting files...

for /f "delims=" %%F in ('git diff --cached --name-only --diff-filter=ACM') do (
    echo %%F | findstr /i /r "\.cpp$ \.hpp$ \.cu$" >nul
    if not errorlevel 1 (
        clang-format -i "%%F"
        git add "%%F"
    )
)

set "BUILD_NEEDED=0"
for /f "delims=" %%F in ('git diff --cached --name-only --diff-filter=ACM') do (
    echo %%F | findstr /i /r "CMakeLists\.txt \.cpp$ \.hpp$ \.cu$ \.cmake$" >nul
    if not errorlevel 1 set "BUILD_NEEDED=1"
)

if "%BUILD_NEEDED%"=="1" (
    echo verifying build...
    cmake -S . -B build
    if errorlevel 1 exit /b 1
    cmake --build build --config Debug
    if errorlevel 1 exit /b 1
) else (
    echo no source files changed, skipping build...
)

echo pre-commit checks passed
endlocal