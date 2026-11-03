# Setup Windows Scheduled Task for NIFTY 50 EOD Post-Market Updates
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$batPath = Join-Path $scriptDir "run_eod_update.bat"

Write-Host "Registering Scheduled Task: NIFTY50_EOD_AutoUpdate"
Write-Host "Target: $batPath"

$action = New-ScheduledTaskAction -Execute $batPath -WorkingDirectory $scriptDir
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At 4:00PM
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

try {
    Register-ScheduledTask -TaskName "NIFTY50_EOD_AutoUpdate" -Action $action -Trigger $trigger -Settings $settings -Description "Runs after NSE market close (4:00 PM IST) to recalculate ML features from the official closing price and forecast the next trading day." -Force | Out-Null
    Write-Host "[SUCCESS] Task 'NIFTY50_EOD_AutoUpdate' registered successfully!" -ForegroundColor Green
    Write-Host "Runs Monday to Friday at 4:00 PM IST."
    Write-Host "If computer was off at 4:00 PM, it will automatically run upon startup!" -ForegroundColor Cyan
} catch {
    Write-Host "[ERROR] Failed to register task: $_" -ForegroundColor Red
}
