# convert_xls_from_csv_nocolumn.ps1
# Prompts for a plain CSV/text file where each row = full .xls file path

# Prompt for CSV file path
$CsvPath = Read-Host "Enter the full path to the file containing .xls paths"
if (-not (Test-Path $CsvPath)) {
    Write-Error "❌ File not found: $CsvPath"
    exit
}

# Read paths line-by-line
$paths = Get-Content $CsvPath | Where-Object { $_.Trim() -ne "" }

$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false

foreach ($xlsPath in $paths) {
    if (-not (Test-Path $xlsPath)) {
        Write-Warning "⚠️ File not found: $xlsPath"
        continue
    }

    $file = Get-Item $xlsPath
    $xlsxPath = "$($file.DirectoryName)\$($file.BaseName).xlsx"

    if (-not (Test-Path $xlsxPath)) {
        try {
            $wb = $excel.Workbooks.Open($xlsPath, 0, $true)
            $wb.SaveAs($xlsxPath, 51)  # 51 = .xlsx format
            $wb.Close($false)
            Write-Output "✅ Converted: $xlsPath → $xlsxPath"
        } catch {
            Write-Warning "❌ Failed: $xlsPath - $_"
        }
    } else {
        Write-Output "🟡 Skipped (already exists): $xlsxPath"
    }
}

$excel.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null

Write-Host "`n🎯 Conversion complete (existing .xlsx files replaced)."
