@echo off

echo ==============================
echo LinkedIn Automation Runner
echo ==============================

:: Get current hour (24-hour format)
for /f "tokens=1 delims=:" %%a in ("%time%") do set HOUR=%%a

:: Remove leading space if any
set HOUR=%HOUR: =%

echo Current Hour: %HOUR%

:: ------------------------------
:: MORNING (5 AM - 11 AM)
:: ------------------------------
if %HOUR% GEQ 5 if %HOUR% LEQ 11 (
    echo 🌅 Running Morning Job (tracker.py)
    python tracker.py
    goto END
)

:: ------------------------------
:: AFTERNOON (12 PM - 5 PM)
:: ------------------------------
if %HOUR% GEQ 12 if %HOUR% LEQ 17 (
    echo 🌆 Running Afternoon Job (inbox.py)
    python inbox.py
    goto END
)

:: ------------------------------
:: EVENING (6 PM - 11 PM)
:: ------------------------------
if %HOUR% GEQ 18 if %HOUR% LEQ 23 (
    echo 🌙 Running Evening Job (followup.py)
    python followup.py
    goto END
)

:: ------------------------------
:: NIGHT (0 AM - 4 AM)
:: ------------------------------
echo 🌑 No job scheduled for this time

:END
echo ==============================
echo Done
pause