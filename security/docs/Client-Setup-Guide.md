# Client Setup Guide
> Simple installation guide for the EMB-255MT software.

---

## Requirements

- Windows 10 / 11 (64-bit)
- Python 3.10
- MySQL Server

---

## Step 1 — Install Python 3.10

Download from:
```
https://www.python.org/downloads/release/python-31011/
```

- Select: **Windows installer (64-bit)**
- ✅ Check **"Add to PATH"**
- ✅ Check **"Install for all users"**
- Click **Install Now**

Verify:
```bash
python --version
# Must show: Python 3.10.x
```

---

## Step 2 — Extract the Software ZIP

Extract the received `EMB-255MT-client.zip` to your preferred folder.

Example:
```
C:\EMB-255MT\
```

---

## Step 3 — Open CMD in Extracted Folder

```
1. Open the extracted folder in File Explorer
2. Click on the address bar
3. Type: cmd
4. Press Enter
```

---

## Step 4 — Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

---

## Step 5 — Install Dependencies

```bash
pip install -r requirements.txt
```

If any error occurs:
```bash
pip install django mysqlclient python-dotenv pillow pymodbus openpyxl weasyprint
```

---

## Step 6 — Configure Database

Open the `.env` file in the extracted folder and update with your MySQL details:

```env
DB_HOST=localhost
DB_NAME=your_database_name
DB_USER=root
DB_PASSWORD=your_password
DB_PORT=3306
```

---

## Step 7 — Run Database Migration (First Time Only)

```bash
python manage.py migrate
```

---

## Step 8 — Start the Software

```bash
python manage.py runserver
```

Open browser and go to:
```
http://localhost:8000
```

---

## Common Issues

| Problem | Fix |
|---|---|
| `python is not recognized` | Reinstall Python 3.10 with "Add to PATH" checked |
| `No module named 'django'` | Run `pip install -r requirements.txt` |
| `No module named 'MySQLdb'` | Run `pip install mysqlclient` |
| `License is not valid` | Contact developer for new license |
| `Can't connect to MySQL` | Check MySQL is running, update .env file |
| Port already in use | Run `python manage.py runserver 8080` |

---

## Contact Developer

If you face any issue not listed above, contact the developer with the **exact error message**.

---

*EMB-255MT Client Setup Guide*
*Python 3.10 | Windows*
