# PowerShell script to organize .md files into docs folder
# Run from the LoudMouth directory

# Create docs folder if it doesn't exist
if (!(Test-Path "docs")) {
    New-Item -ItemType Directory -Path "docs"
}

# Move .md files to docs (except README.md which should stay in root)
$mdFiles = @(
    "MODEL_STATUS_UPDATE_FIX.md",
    "MODEL_STATUS_UPDATE_IMPROVEMENTS.md", 
    "SETTINGS_MANAGER_DESIGN.md"
)

foreach ($file in $mdFiles) {
    if (Test-Path $file) {
        Write-Host "Moving $file to docs folder..."
        Move-Item -Path $file -Destination "docs\$file" -Force
    } else {
        Write-Host "$file not found, skipping..."
    }
}

Write-Host "`nFiles moved successfully!"
Write-Host "README.md remains in root directory (standard practice)"

# List contents of docs folder
Write-Host "`nContents of docs folder:"
Get-ChildItem "docs" | Format-Table Name, LastWriteTime -AutoSize