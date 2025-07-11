@echo off
echo Organizing .md files into docs folder...

REM Move documentation files to docs folder
if exist "MODEL_STATUS_UPDATE_FIX.md" (
    echo Moving MODEL_STATUS_UPDATE_FIX.md...
    move /Y "MODEL_STATUS_UPDATE_FIX.md" "docs\"
)

if exist "MODEL_STATUS_UPDATE_IMPROVEMENTS.md" (
    echo Moving MODEL_STATUS_UPDATE_IMPROVEMENTS.md...
    move /Y "MODEL_STATUS_UPDATE_IMPROVEMENTS.md" "docs\"
)

if exist "SETTINGS_MANAGER_DESIGN.md" (
    echo Moving SETTINGS_MANAGER_DESIGN.md...
    move /Y "SETTINGS_MANAGER_DESIGN.md" "docs\"
)

echo.
echo Files moved successfully!
echo README.md remains in root directory (standard practice)
echo.
echo Contents of docs folder:
dir /B docs\*.md
pause