@echo off
chcp 65001 > nul
echo ========================================================
echo        TCAS Mastery Prep System - กำลังเปิดระบบ
echo ========================================================
echo.
echo ระบบทำงานแบบ Local-First บนเครื่องคอมพิวเตอร์ของคุณ
echo กำลังเริ่มต้นเซิร์ฟเวอร์ที่ http://127.0.0.1:8000 ...
echo (กด Ctrl+C เพื่อหยุดการทำงาน)
echo.

python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
pause
