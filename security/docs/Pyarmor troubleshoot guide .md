# PyArmor 7.7.4 — Problems & Solutions Guide
> All real-world errors encountered during Django project encryption and their exact fixes.

---

## Problem 1 — PyArmor 9 Trial Limitation

### Error
```
Pyarmor 9.2.3 (trial), non-profits
Notes: Can't obfuscate big script and mix str
```

### Cause
PyArmor 9 trial version cannot encrypt large Python files. Big service files, views, and models will be skipped or fail silently.

### Fix
Downgrade to PyArmor 7.7.4 — fully free, no restrictions:
```bash
pip uninstall pyarmor -y
pip install pyarmor==7.7.4
```

Verify:
```bash
pyarmor --version
# PyArmor Trial Version 7.7.4
```

> ✅ "Trial Version" in PyArmor 7 = No restrictions. All features work free.

---

## Problem 2 — Python 3.11+ Not Supported

### Error
```
ERROR    Python 3.11+ is not supported now
```

### Cause
PyArmor 7.7.4 only supports Python 3.10 and below. Running it on Python 3.11 or 3.12 throws this error immediately.

### Fix
Install Python 3.10 alongside your existing Python:

```
Download: https://www.python.org/downloads/release/python-31011/
Select: Windows installer (64-bit)
Install to: C:\Python310
Uncheck "Add to PATH" (to avoid conflict with existing Python)
```

Create a separate venv using Python 3.10:
```bash
C:\Python310\python.exe -m venv venv310
venv310\Scripts\activate
python --version
# Must show: Python 3.10.x
```

> ✅ Your original Python 3.11 is NOT removed — both versions exist side by side.

---

## Problem 3 — Wrong dist/ Structure (Everything Dumped in Root)

### Error
```
ModuleNotFoundError: No module named 'flowserve_soft'
```

### Cause
Running `pyarmor obfuscate --recursive` multiple times without `--output` flag causes each command to overwrite the previous output. All files end up in dist/ root instead of their correct subfolders.

### Wrong Command (causes this issue)
```bash
# ❌ WRONG — overwrites previous output
pyarmor obfuscate --recursive flowserve_app/__init__.py
pyarmor obfuscate --recursive flowserve_soft/__init__.py
```

### Fix
Always use `--output` flag with correct subfolder path:

```bash
# Delete broken dist/
rmdir /s /q dist

# ✅ CORRECT — each output goes to correct subfolder
pyarmor obfuscate --recursive --output dist/flowserve_app flowserve_app/__init__.py
pyarmor obfuscate --recursive --output dist/flowserve_soft flowserve_soft/__init__.py
pyarmor obfuscate --output dist manage.py
```

Verify structure after:
```bash
dir dist
dir dist\flowserve_app
dir dist\flowserve_soft
```

---

## Problem 4 — views/ Folder Not Encrypted

### Error
```
ModuleNotFoundError: No module named 'flowserve_app.views'
```

### Cause
The `views/` folder inside `flowserve_app` was not included in the encryption command. PyArmor only encrypted `__init__.py` and files at the top level.

### Fix
Encrypt views separately with correct output path:
```bash
pyarmor obfuscate --recursive --output dist/flowserve_app/views flowserve_app/views/__init__.py
```

Verify:
```bash
dir dist\flowserve_app
# Must show views/ folder
```

---

## Problem 5 — Django Not Installed in New venv

### Error
```
ModuleNotFoundError: No module named 'django'
Couldn't import Django. Are you sure it's installed?
```

### Cause
A new venv (venv310) was created for Python 3.10 but project dependencies were not installed in it. Each venv is isolated — packages from other venvs don't carry over.

### Fix
```bash
# Make sure venv310 is activated
venv310\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

If requirements.txt fails due to version conflicts:
```bash
pip install django mysqlclient python-dotenv pillow pymodbus openpyxl weasyprint matplotlib numpy
```

---

## Problem 6 — contourpy Build Failed (Python Version Mismatch)

### Error
```
ERROR: Could not find a version that satisfies the requirement contourpy==1.3.3
contourpy==1.3.3 Requires-Python >=3.11
```

### Cause
`requirements.txt` was generated on Python 3.11. Some packages in it require Python 3.11+ and won't install on Python 3.10.

### Fix — Option A (Try ignore flag first)
```bash
pip install -r requirements.txt --ignore-requires-python
```

### Fix — Option B (Install core packages manually)
```bash
pip install django mysqlclient python-dotenv pillow pymodbus openpyxl weasyprint matplotlib numpy sqlparse
```

> ✅ You don't need exact versions for the encrypted dist/ to work — just the correct packages.

---

## Problem 7 — MySQLdb Module Not Found

### Error
```
ModuleNotFoundError: No module named 'MySQLdb'
django.core.exceptions.ImproperlyConfigured: Error loading MySQLdb module.
Did you install mysqlclient?
```

### Cause
`mysqlclient` package not installed in the current venv.

### Fix
```bash
pip install mysqlclient
```

---

## Problem 8 — dotenv Module Not Found

### Error
```
ModuleNotFoundError: No module named 'dotenv'
```

### Cause
`python-dotenv` package not installed. Note: the import name is `dotenv` but the package name is `python-dotenv`.

### Fix
```bash
pip install python-dotenv
```

---

## Problem 9 — pytransform Runtime Missing

### Error
```
ModuleNotFoundError: No module named 'pytransform'
```

### Cause
The `pytransform/` folder (PyArmor runtime engine) is missing from dist/. This folder is required for all encrypted files to run.

### Fix
Re-run the encryption — pytransform/ is auto-generated:
```bash
pyarmor obfuscate --recursive --output dist/flowserve_app flowserve_app/__init__.py
```

Check it exists:
```bash
dir dist
dir dist\flowserve_app
# Must show pytransform/ in each encrypted folder
```

> ⚠️ Never delete pytransform/ folder — encrypted code cannot run without it.

---

## Problem 10 — License Not Valid / Wrong Machine

### Error
```
License is expired or not valid
RuntimeError: protection exception (2)
```

### Cause
The `license.lic` file was generated for a different machine. Each license is hardware-bound and only works on the specific machine it was generated for.

### Fix
Re-generate license with the correct machine's hardware ID:

```bash
# Step 1 — Get correct machine ID (run ON that machine)
pyarmor hdinfo

# Step 2 — Generate new license (on YOUR machine)
pyarmor licenses --expired 2027-12-31 --bind-disk "CORRECT_DISK_SERIAL" client001

# Step 3 — Copy to dist/
copy licenses\client001\license.lic dist\
```

---

## Problem 11 — License File Missing

### Error
```
RuntimeError: protection exception (1)
```

### Cause
`license.lic` file is missing from the dist/ folder. The encrypted code requires a license file to run.

### Fix
```bash
# Generate license
pyarmor licenses --expired 2027-12-31 --bind-disk "DISK_SERIAL" client001

# Place in same folder as manage.py
copy licenses\client001\license.lic dist\

# Verify it's there
dir dist
# Must show license.lic
```

---

## Problem 12 — Templates Not Found

### Error
```
TemplateDoesNotExist: dashboard.html
```

### Cause
HTML template files were not copied into dist/ after encryption. PyArmor only copies `.py` files.

### Fix
```bash
xcopy flowserve_app\templates dist\flowserve_app\templates /E /I /Y
```

---

## Problem 13 — Static Files 404

### Error
```
GET /static/css/style.css HTTP/1.1 404
```

### Cause
Static files (CSS, JS, images) were not copied into dist/ after encryption.

### Fix
```bash
xcopy flowserve_app\static dist\flowserve_app\static /E /I /Y
```

---

## Problem 14 — Port Already in Use

### Error
```
Error: That port is already in use.
```

### Cause
Port 8000 is already occupied by another process.

### Fix
```bash
# Run on different port
python manage.py runserver 8080

# OR find and kill the process using port 8000
netstat -ano | findstr :8000
taskkill /PID <PID_NUMBER> /F
```

---

## Problem 15 — Database Connection Error

### Error
```
django.db.utils.OperationalError: (2003) Can't connect to MySQL server
```

### Cause
`.env` file has developer machine's database credentials — not client's database.

### Fix
Update `.env` file in dist/ with client machine's database details:
```env
DB_HOST=localhost
DB_NAME=your_database_name
DB_USER=root
DB_PASSWORD=client_db_password
DB_PORT=3306
```

---

## Quick Reference — All Errors at a Glance

| Error Message | Fix |
|---|---|
| `Can't obfuscate big script` | Downgrade to PyArmor 7.7.4 |
| `Python 3.11+ is not supported` | Create venv with Python 3.10 |
| `No module named 'flowserve_soft'` | Use `--output` flag, re-encrypt |
| `No module named 'flowserve_app.views'` | Encrypt views/ folder separately |
| `No module named 'django'` | `pip install -r requirements.txt` |
| `No module named 'MySQLdb'` | `pip install mysqlclient` |
| `No module named 'dotenv'` | `pip install python-dotenv` |
| `No module named 'pytransform'` | Re-encrypt, keep pytransform/ folder |
| `protection exception (1)` | Place license.lic next to manage.py |
| `protection exception (2)` | Regenerate license for correct machine |
| `TemplateDoesNotExist` | `xcopy templates into dist/` |
| Static files 404 | `xcopy static into dist/` |
| Port already in use | `python manage.py runserver 8080` |
| Can't connect to MySQL | Update .env with correct DB credentials |
| `contourpy requires Python >=3.11` | `pip install -r requirements.txt --ignore-requires-python` |

---

## Checklist Before Sending to Client

```
✅ Python 3.10 used for encryption
✅ dist/flowserve_app/ exists and encrypted
✅ dist/flowserve_soft/ exists and encrypted
✅ dist/flowserve_app/views/ exists and encrypted
✅ pytransform/ folder present in dist/ and subfolders
✅ templates/ copied into dist/flowserve_app/
✅ static/ copied into dist/flowserve_app/
✅ license.lic in same folder as manage.py
✅ license.lic generated for CLIENT machine (not your machine)
✅ .env file copied with correct DB credentials
✅ requirements.txt copied to dist/
✅ Tested on client machine before final handover
```

---

*Troubleshoot Guide — EMB-255MT Django HMI Project*
*PyArmor 7.7.4 | Python 3.10 | Windows*