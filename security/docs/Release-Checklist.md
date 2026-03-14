# Release Checklist
> Complete this checklist before every client delivery. No step can be skipped.

---

## PHASE 1 — Encryption Check

- [ ] Python 3.10 venv (venv310) is activated
- [ ] PyArmor 7.7.4 is installed (`pyarmor --version`)
- [ ] `dist/` folder deleted before fresh encryption
- [ ] `flowserve_app/` encrypted with correct `--output dist/flowserve_app`
- [ ] `flowserve_soft/` encrypted with correct `--output dist/flowserve_soft`
- [ ] `flowserve_app/views/` encrypted with correct `--output dist/flowserve_app/views`
- [ ] `manage.py` encrypted with `--output dist`

---

## PHASE 2 — dist/ Structure Check

- [ ] `dist/flowserve_app/` exists
- [ ] `dist/flowserve_app/migrations/` exists
- [ ] `dist/flowserve_app/services/` exists
- [ ] `dist/flowserve_app/views/` exists
- [ ] `dist/flowserve_app/urls/` exists
- [ ] `dist/flowserve_app/templatetags/` exists
- [ ] `dist/flowserve_soft/` exists
- [ ] `dist/manage.py` exists
- [ ] `dist/pytransform/` exists ← CRITICAL
- [ ] `dist/flowserve_app/pytransform/` exists ← CRITICAL
- [ ] `dist/flowserve_soft/pytransform/` exists ← CRITICAL

---

## PHASE 3 — Static & Template Files Check

- [ ] `dist/flowserve_app/templates/` exists and has HTML files
- [ ] `dist/flowserve_app/static/css/` exists
- [ ] `dist/flowserve_app/static/images/` exists
- [ ] `dist/flowserve_app/static/scripts/` exists
- [ ] `dist/flowserve_app/static/vendor/` exists

---

## PHASE 4 — Root Files Check

- [ ] `dist/requirements.txt` copied
- [ ] `dist/.env` copied
- [ ] `dist/FP-80MT.bat` copied
- [ ] `dist/tssx-icon (1).ico` copied

---

## PHASE 5 — License Check

- [ ] Client machine ID (disk serial) received from client
- [ ] License generated for correct client machine
- [ ] License expiry date set correctly
- [ ] `dist/license.lic` is present
- [ ] `license.lic` is in same folder as `manage.py`
- [ ] Client record table updated with new license info
- [ ] License backed up in `licenses/clientXXX/` folder

---

## PHASE 6 — Local Test Check

- [ ] Tested `python manage.py runserver` from dist/ folder
- [ ] Server starts without errors
- [ ] Login page loads in browser
- [ ] Dashboard loads correctly
- [ ] No 404 errors for static files
- [ ] Database connects successfully

---

## PHASE 7 — Final Package Check

- [ ] ZIP created: `EMB-255MT-clientXXX.zip`
- [ ] ZIP contains all dist/ contents
- [ ] ZIP contains correct client's `license.lic`
- [ ] ZIP does NOT contain `venv310/` folder
- [ ] ZIP does NOT contain original source code
- [ ] ZIP does NOT contain `.pyarmor/` folder

---

## PHASE 8 — Client Delivery

- [ ] ZIP sent to client
- [ ] Client Setup Guide sent to client
- [ ] Client confirmed extraction successful
- [ ] Client confirmed server running
- [ ] Client confirmed login working
- [ ] Delivery date recorded

---

## Client Delivery Record

| Client | Version | Delivery Date | License Expiry | Notes |
|---|---|---|---|---|
| | | | | |

---

> ✅ All boxes checked = Safe to deliver
> ❌ Any box unchecked = Do NOT deliver yet

---

*Release Checklist — EMB-255MT*
*PyArmor 7.7.4 | Windows*
