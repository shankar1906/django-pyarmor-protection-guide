# Django Project Protection Guide — PyArmor 7.7.4
> Complete step-by-step guide to encrypt and protect a Django project using PyArmor 7.7.4 with machine-bound license.

---

## Requirements

| Item | Version |
|---|---|
| Python | 3.10.x (PyArmor 7 does NOT support 3.11+) |
| PyArmor | 7.7.4 |
| OS | Windows |

---

## Overview

```
YOUR MACHINE                        CLIENT MACHINE
────────────────────────────        ──────────────────────────
Install Python 3.10                 Install Python 3.10
Install PyArmor 7.7.4               Install dependencies
Encrypt project                     Receive ZIP from developer
Get client machine ID       ←───    Send machine ID
Generate machine-bound key
ZIP dist/ → send to client  ────→   Extract ZIP
                                    Run python manage.py runserver ✅
```

---

## PHASE 1 — Developer Machine Setup

---

### Step 1 — Install Python 3.10

> ⚠️ PyArmor 7.7.4 only supports Python 3.10 and below. Python 3.11+ will throw an error.

Download Python 3.10 from:
```
https://www.python.org/downloads/release/python-31011/
```

- Select: **Windows installer (64-bit)**
- During install: **Uncheck "Add to PATH"** (to avoid conflicting with existing Python)
- Install to: `C:\Python310`

Verify:
```bash
C:\Python310\python.exe --version
# Python 3.10.x
```

---

### Step 2 — Create Virtual Environment with Python 3.10

```bash
cd d:\your-project\

# Create venv using Python 3.10
C:\Python310\python.exe -m venv venv310

# Activate it
venv310\Scripts\activate
```

Verify:
```bash
python --version
# Python 3.10.x
```

---

### Step 3 — Install PyArmor 7.7.4

```bash
pip install pyarmor==7.7.4
```

Verify:
```bash
pyarmor --version
# PyArmor Trial Version 7.7.4
```

> ✅ "Trial Version" in PyArmor 7 = No restrictions. All features work free.

---

### Step 4 — Install Project Dependencies

```bash
pip install -r requirements.txt
```

If any package fails due to Python version conflict:
```bash
pip install django mysqlclient python-dotenv pillow pymodbus openpyxl weasyprint matplotlib numpy
```

---

### Step 5 — Encrypt the Project

Run each command one by one:

```bash
# Encrypt flowserve_app
pyarmor obfuscate --recursive --output dist/flowserve_app flowserve_app/__init__.py

# Encrypt flowserve_soft (settings, urls, wsgi)
pyarmor obfuscate --recursive --output dist/flowserve_soft flowserve_soft/__init__.py

# Encrypt views separately
pyarmor obfuscate --recursive --output dist/flowserve_app/views flowserve_app/views/__init__.py

# Encrypt manage.py
pyarmor obfuscate --output dist manage.py
```

Verify structure:
```bash
dir dist
dir dist\flowserve_app
dir dist\flowserve_soft
```

Expected output:
```
dist/
  ├── flowserve_app/
  │   ├── migrations/      ← encrypted
  │   ├── services/        ← encrypted
  │   ├── views/           ← encrypted
  │   ├── urls/            ← encrypted
  │   ├── templatetags/    ← encrypted
  │   ├── models.py        ← encrypted
  │   └── pytransform/     ← runtime (DO NOT DELETE)
  ├── flowserve_soft/
  │   ├── settings.py      ← encrypted
  │   ├── wsgi.py          ← encrypted
  │   ├── urls.py          ← encrypted
  │   └── pytransform/     ← runtime (DO NOT DELETE)
  ├── pytransform/         ← runtime (DO NOT DELETE)
  └── manage.py            ← encrypted
```

---

### Step 6 — Copy Non-Python Files into dist/

PyArmor only encrypts `.py` files. Static files and templates must be copied manually.

```bash
# Copy templates
xcopy flowserve_app\templates dist\flowserve_app\templates /E /I /Y

# Copy static files (CSS, JS, Images, Videos)
xcopy flowserve_app\static dist\flowserve_app\static /E /I /Y

# Copy root files
copy requirements.txt dist\
copy FP-80MT.bat dist\
copy "tssx-icon (1).ico" dist\
copy .env dist\
```

---

### Step 7 — Test Encrypted Project on Your Machine

First generate a license for your own machine:

```bash
# Get your machine ID
pyarmor hdinfo

# Generate license for your machine
pyarmor licenses --expired 2027-12-31 --bind-disk "YOUR_DISK_SERIAL" devtest

# Copy license to dist/
copy licenses\devtest\license.lic dist\
```

Run the server:
```bash
cd dist
python manage.py runserver
```

✅ If server starts — encryption is working correctly.

---

## PHASE 2 — Get Client Machine ID

Go to **client's machine** and run:

```bash
# Install PyArmor on client machine
pip install pyarmor==7.7.4

# Get hardware info
pyarmor hdinfo
```

Output example:
```
Default Harddisk Serial Number: 'BLH2-3924'
Default Mac address: 'f8:75:a4:xx:xx:xx'
Machine ID: 'xxxxxxxxxxxxxxxx'
```

**Client sends you the Harddisk Serial Number or MAC address.**

---

## PHASE 3 — Generate Client License

Back on your machine:

```bash
cd d:\your-project\

# Using Hard disk serial (recommended)
pyarmor licenses --expired 2027-12-31 --bind-disk "CLIENT_DISK_SERIAL" client001

# OR using MAC address
pyarmor licenses --expired 2027-12-31 --bind-mac "CLIENT_MAC_ADDRESS" client001
```

This creates:
```
licenses/
  └── client001/
        └── license.lic    ← machine-bound secret key
```

Copy license to dist/:
```bash
copy licenses\client001\license.lic dist\
```

---

## PHASE 4 — Package and Send to Client

### Final dist/ Structure

```
dist/
  ├── flowserve_app/
  │   ├── migrations/
  │   ├── services/
  │   ├── views/
  │   ├── urls/
  │   ├── templates/       ← copied HTML
  │   ├── static/          ← copied CSS/JS/Images
  │   ├── pytransform/     ← DO NOT DELETE
  │   └── ...encrypted .py files
  ├── flowserve_soft/
  │   ├── pytransform/     ← DO NOT DELETE
  │   └── ...encrypted .py files
  ├── pytransform/         ← DO NOT DELETE
  ├── manage.py
  ├── license.lic          ← client machine-bound key
  ├── requirements.txt
  ├── FP-80MT.bat
  ├── .env
  └── tssx-icon (1).ico
```

### ZIP the dist/ folder

```bash
cd d:\your-project\
powershell Compress-Archive -Path dist\* -DestinationPath ProjectName-client.zip
```

Send `ProjectName-client.zip` to client.

---

## PHASE 5 — Client Installation

### Step 1 — Install Python 3.10

```
https://www.python.org/downloads/release/python-31011/
```

- Select: **Windows installer (64-bit)**
- ✅ Check "Add to PATH"
- ✅ Check "Install for all users"

### Step 2 — Extract ZIP and Setup

```bash
# Extract the ZIP
# Open CMD in extracted folder

# Create virtual environment
python -m venv venv

# Activate
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations (first time only)
python manage.py migrate

# Start server
python manage.py runserver
```

✅ Software runs — only on that specific machine.

---

## PHASE 6 — For Every New Client

Only 3 things to do per new client:

```bash
# 1. Get their machine ID (on their PC)
pyarmor hdinfo

# 2. Generate their unique license (on your PC)
pyarmor licenses --expired 2027-12-31 --bind-disk "NEW_CLIENT_DISK_SERIAL" client002

# 3. Copy new license to dist/
copy licenses\client002\license.lic dist\

# 4. ZIP and send
powershell Compress-Archive -Path dist\* -DestinationPath ProjectName-client002.zip
```

> The encrypted dist/ code stays the same — only `license.lic` changes per client.

---

## Troubleshoot Reference

| Error | Cause | Fix |
|---|---|---|
| `Python 3.11+ is not supported` | Wrong Python version | Use Python 3.10 venv |
| `No module named 'pytransform'` | Runtime folder missing | Ensure `pytransform/` exists in dist/ |
| `License is expired or not valid` | Wrong machine license | Regenerate license with correct machine ID |
| `No module named 'django'` | Dependencies not installed | `pip install -r requirements.txt` |
| `No module named 'MySQLdb'` | MySQL client missing | `pip install mysqlclient` |
| `No module named 'dotenv'` | dotenv missing | `pip install python-dotenv` |
| `No module named 'flowserve_app.views'` | views/ not encrypted | Re-run views encryption step |
| `No module named 'flowserve_soft'` | Wrong dist/ structure | Re-run all encryption steps |
| Template not found | Templates not copied | Re-run xcopy templates step |
| Static files 404 | Static not copied | Re-run xcopy static step |
| Database connection error | Wrong DB credentials | Update .env file with client DB info |
| Port already in use | Port 8000 busy | `python manage.py runserver 8080` |

---

## Security Summary

| Threat | Protected? |
|---|---|
| Read source code | ✅ Fully encrypted binary |
| Copy to another machine | ✅ License bound to hardware |
| Run with expired license | ✅ Blocked after expiry date |
| AI decoding | ✅ Binary — nothing readable |
| Casual reverse engineering | ✅ Blocked |
| Hardcore reverse engineering | ⚠️ Very difficult, not impossible |
| Internal source code leak | ❌ Keep original source safe yourself |

---

## Important Notes

- ✅ **Original source code** is never touched — always stays on your machine
- ✅ Each client gets a **unique license** — one client's license won't work on another machine
- ✅ Never share the **original project folder** — only send `dist/` contents
- ✅ Never share **venv310** — client creates their own venv
- ✅ `pytransform/` folder **must always** be present in dist/ — never delete it
- ✅ `license.lic` must be in the **same folder as manage.py**
- ⚠️ When license expires — generate new key with updated `-e` date and resend

---

*Guide prepared for EMB-255MT Django HMI Project*
*PyArmor 7.7.4 | Python 3.10 | Windows*