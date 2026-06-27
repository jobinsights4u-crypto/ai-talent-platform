@echo off
echo Cleaning old page files from previous versions...
cd pages
del /Q "0_*.py" 2>nul
del /Q "0b_*.py" 2>nul
del /Q "1_*.py" 2>nul
del /Q "2_*.py" 2>nul
del /Q "2b_*.py" 2>nul
del /Q "3_*.py" 2>nul
del /Q "4_*.py" 2>nul
del /Q "4b_*.py" 2>nul
del /Q "5_*.py" 2>nul
del /Q "6_*.py" 2>nul
del /Q "7_*.py" 2>nul
del /Q "8_*.py" 2>nul
del /Q "9_*.py" 2>nul
cd ..
echo Done. Now re-extract the v4 zip and run: python -m streamlit run app.py
pause
