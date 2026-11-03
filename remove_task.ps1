# Unregister Windows Scheduled Task for NIFTY 50
try {
    Unregister-ScheduledTask -TaskName "NIFTY50_EOD_AutoUpdate" -Confirm:$false
    Write-Host "[SUCCESS] Task 'NIFTY50_EOD_AutoUpdate' has been removed." -ForegroundColor Green
} catch {
    Write-Host "[INFO] Task was not found or already removed." -ForegroundColor Yellow
}
