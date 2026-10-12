@echo off
echo ========================================================
echo  Starting Health Copilot AI (Backend + Frontend)
echo ========================================================

echo [1/2] Launching FastAPI Backend on http://127.0.0.1:8000 ...
start "Health Copilot - Backend API" cmd /k ".\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000"

timeout /t 2 /nobreak >nul

echo [2/2] Launching Frontend on http://localhost:5173 ...
cd frontend
start "Health Copilot - Frontend App" cmd /k "npm run dev"
cd ..

timeout /t 3 /nobreak >nul
start http://localhost:5173

echo.
echo ========================================================
echo  Both servers are running!
echo  Frontend UI:  http://localhost:5173
echo  Backend API:  http://127.0.0.1:8000
echo  Swagger Docs: http://127.0.0.1:8000/docs
echo ========================================================
