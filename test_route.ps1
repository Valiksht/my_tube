try {
    $r = Invoke-WebRequest -Uri 'http://127.0.0.1:8000/channel/create' -UseBasicParsing
    Write-Output "HTTP/$($r.Version)"
    Write-Output "Status: $($r.StatusCode)"
    Write-Output "Headers:"
    $r.Headers | ForEach-Object { Write-Output "  $_" }
    Write-Output "Body:"
    Write-Output $r.Content
} catch {
    Write-Output "Error: $($_.Exception.Message)"
    if ($_.Exception.Response) {
        Write-Output "Status: $($_.Exception.Response.StatusCode.value__)"
    }
}
