REM echo python flask is running...
REM start cmd /k "python -u index.py > NUL 2>&1"

set FLASK_APP=index.py
python -m flask --no-debug run 