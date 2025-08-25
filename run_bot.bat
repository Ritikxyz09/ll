@echo off
echo Setting up virtual environment...
python -m venv mybotenv
call mybotenv\Scripts\activate

echo Installing requirements...
pip install -r requirements.txt

echo Starting bot...
python otp_bot.py
pause
