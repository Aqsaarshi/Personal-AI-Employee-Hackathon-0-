# LinkedIn Auto Poster - PowerShell Task Scheduler Setup
# Creates a scheduled task to post to LinkedIn daily at 9 AM

$taskName = "LinkedIn Auto Poster"
$scriptPath = Join-Path $PSScriptRoot "auto_linkedin_poster.py"
$pythonExe = (Get-Command python -ErrorAction SilentlyContinue).Source

if (-not $pythonExe) {
    Write-Host "ERROR: Python not found in PATH!" -ForegroundColor Red
    Write-Host "Please install Python or add it to your system PATH." -ForegroundColor Yellow
    exit 1
}

Write-Host "============================================" -ForegroundColor Cyan
Write-Host " LinkedIn Auto Poster - Task Scheduler Setup" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Python found: $pythonExe" -ForegroundColor Green
Write-Host "Script location: $scriptPath" -ForegroundColor Green
Write-Host ""

# Remove existing task if it exists
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "Removing existing task..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

# Create task trigger (daily at 9 AM)
$trigger = New-ScheduledTaskTrigger -Daily -At 9am

# Create task action
$action = New-ScheduledTaskAction -Execute $pythonExe -Argument "`"$scriptPath`"" -WorkingDirectory $PSScriptRoot

# Create task settings
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -WakeToRun

# Create task principal (run with highest privileges)
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U -RunLevel Highest

# Register the task
try {
    Register-ScheduledTask `
        -TaskName $taskName `
        -Trigger $trigger `
        -Action $action `
        -Settings $settings `
        -Principal $principal `
        -Description "Automatically posts business content to LinkedIn daily" `
        -ErrorAction Stop
    
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Green
    Write-Host " SUCCESS! Task created successfully." -ForegroundColor Green
    Write-Host "============================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your LinkedIn posts will be published daily at 9:00 AM." -ForegroundColor White
    Write-Host ""
    Write-Host "To run the task manually:" -ForegroundColor Cyan
    Write-Host "  Start-ScheduledTask -TaskName 'LinkedIn Auto Poster'" -ForegroundColor Gray
    Write-Host ""
    Write-Host "To view task history:" -ForegroundColor Cyan
    Write-Host "  Open Task Scheduler > Task Scheduler Library > LinkedIn Auto Poster > History" -ForegroundColor Gray
    Write-Host ""
    Write-Host "To remove the task:" -ForegroundColor Cyan
    Write-Host "  Unregister-ScheduledTask -TaskName 'LinkedIn Auto Poster' -Confirm:`$false" -ForegroundColor Gray
    Write-Host ""
}
catch {
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Red
    Write-Host " ERROR! Failed to create task." -ForegroundColor Red
    Write-Host "============================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please run this script as Administrator." -ForegroundColor Yellow
    Write-Host ""
}
