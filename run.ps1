Write-Host "========================================================" -ForegroundColor Cyan
Write-Host " Starting Health Copilot AI (Backend + Frontend)" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Cyan

Write-Host "[1/2] Launching FastAPI Backend on http://127.0.0.1:8000 ..." -ForegroundColor Yellow
Start-Process -FilePath "cmd.exe" -ArgumentList '/k ".\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000"'

Start-Sleep -Seconds 2

Write-Host "[2/2] Launching Frontend on http://localhost:5173 ..." -ForegroundColor Yellow
Start-Process -FilePath "cmd.exe" -ArgumentList '/k "cd frontend && npm run dev"'

Start-Sleep -Seconds 3

Start-Process "http://localhost:5173"

Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host " Both servers are running!" -ForegroundColor Green
Write-Host " Frontend UI:  http://localhost:5173" -ForegroundColor Cyan
Write-Host " Backend API:  http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host " Swagger Docs: http://127.0.0.1:8000/docs" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
