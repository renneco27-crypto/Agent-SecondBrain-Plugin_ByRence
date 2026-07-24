@echo off
setlocal enabledelayedexpansion

echo ===================================================
echo     OPENCODE SECOND-BRAIN SETUP FOR WINDOWS
echo ===================================================
echo.

:: Source templates
set "SOURCE=C:\Users\corte\Documents\do not delete second brain"

:: Prompt for target project path
set /p "TARGET_PATH=Enter or paste your project directory path: "

:: Strip double quotes (drag-and-drop from Explorer adds them)
set "TARGET_PATH=%TARGET_PATH:"=%"

:: Validate
if not exist "%TARGET_PATH%" (
    echo.
    echo [ERROR] "%TARGET_PATH%" does not exist.
    pause
    exit /b 1
)
echo [1/4] Target: %TARGET_PATH%

:: Create .opencode\memory directory
echo [2/4] Creating .opencode\memory...
if not exist "%TARGET_PATH%\.opencode" mkdir "%TARGET_PATH%\.opencode"
if not exist "%TARGET_PATH%\.opencode\memory" mkdir "%TARGET_PATH%\.opencode\memory"

:: Create memory\functions.md if not exists
if not exist "%TARGET_PATH%\memory\functions.md" (
    type nul > "%TARGET_PATH%\memory\functions.md"
)

:: Copy AGENTS.md
copy /Y "%SOURCE%\AGENTS.md" "%TARGET_PATH%\AGENTS.md" >nul

:: Ensure .gitignore exists with sensible defaults
if not exist "%TARGET_PATH%\.gitignore" (
    (
        echo node_modules/
        echo .env
        echo .env.local
        echo .env*.local
        echo .next/
        echo dist/
        echo build/
        echo *.zip
    ) > "%TARGET_PATH%\.gitignore"
    echo [INFO] Created .gitignore with defaults
) else (
    echo [SKIP] .gitignore already exists
)

:: Copy opencode.json (only if target doesn't have one)
if not exist "%TARGET_PATH%\opencode.json" (
    copy /Y "%SOURCE%\opencode.json" "%TARGET_PATH%\opencode.json" >nul
) else (
    echo [SKIP] opencode.json already exists — not overwriting
)

:: Copy plugin .ts files into project's .opencode/plugins/
set "TOOL_DIR=%USERPROFILE%\.config\opencode\skills\tools"
if exist "%TOOL_DIR%" (
    if not exist "%TARGET_PATH%\.opencode\plugins" mkdir "%TARGET_PATH%\.opencode\plugins"

    for %%F in (smart_read.ts semantic_chunk.ts semantic_diff.ts) do (
        if exist "%TOOL_DIR%\%%F" (
            if not exist "%TARGET_PATH%\.opencode\plugins\%%F" (
                copy /Y "%TOOL_DIR%\%%F" "%TARGET_PATH%\.opencode\plugins\%%F" >nul
                echo [INFO] Copied %%F to .opencode\plugins\
            ) else (
                echo [SKIP] %%F already exists
            )
        ) else (
            echo [SKIP] %%F not found at %TOOL_DIR%
        )
    )
) else (
    echo [SKIP] Tool directory %TOOL_DIR% not found
)

echo [4/4] Installing OpenCode plugin dependencies...
:: -------------------------------------------------------
:: Check for pnpm, install plugin deps if package.json exists
:: -------------------------------------------------------
if exist "%TARGET_PATH%\package.json" (
    where pnpm >nul 2>&1
    if errorlevel 1 (
        echo [WARN] pnpm not found in PATH. Install manually:
        echo        cd /d "%TARGET_PATH%"
        echo        pnpm add @opencode-ai/plugin
        echo        pnpm add web-tree-sitter
        echo        pnpm add @tree-sitter-grammars/tree-sitter-typescript
        echo        pnpm add @tree-sitter-grammars/tree-sitter-python
    ) else (
        pushd "%TARGET_PATH%"

        findstr /C:"@opencode-ai/plugin" package.json >nul 2>&1
        if errorlevel 1 (
            echo [INFO] Installing @opencode-ai/plugin...
            call pnpm add @opencode-ai/plugin
        ) else (
            echo [SKIP] @opencode-ai/plugin already installed
        )

        findstr /C:"web-tree-sitter" package.json >nul 2>&1
        if errorlevel 1 (
            echo [INFO] Installing web-tree-sitter...
            call pnpm add web-tree-sitter
        ) else (
            echo [SKIP] web-tree-sitter already installed
        )

        findstr /C:"tree-sitter-typescript" package.json >nul 2>&1
        if errorlevel 1 (
            echo [INFO] Installing tree-sitter-typescript grammar...
            call pnpm add @tree-sitter-grammars/tree-sitter-typescript
        ) else (
            echo [SKIP] tree-sitter-typescript already installed
        )

        findstr /C:"tree-sitter-python" package.json >nul 2>&1
        if errorlevel 1 (
            echo [INFO] Installing tree-sitter-python grammar...
            call pnpm add @tree-sitter-grammars/tree-sitter-python
        ) else (
            echo [SKIP] tree-sitter-python already installed
        )

        popd
    )
) else (
    echo [SKIP] No package.json found — skipping dependency install
)

echo.
echo ===================================================
echo   SUCCESS! Second-brain setup completed for:
echo   %TARGET_PATH%
echo ===================================================
echo   Files deployed/verified:
echo     AGENTS.md                    (memory directives)
echo     opencode.json                (opencode config)
echo     .opencode\memory\            (for functions.md)
echo     .opencode\plugins\           (smart_read, semantic_chunk, semantic_diff tools)
echo     memory\functions.md          (function knowledge base)
echo     .gitignore                   (scan exclusion rules)
echo     pnpm dependencies            (@opencode-ai/plugin, web-tree-sitter, tree-sitter grammars)
echo ===================================================
pause
