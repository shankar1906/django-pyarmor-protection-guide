# License Management Guide
> How to manage PyArmor licenses for multiple clients.

---

## License Basics

| Item | Detail |
|---|---|
| License file name | `license.lic` |
| Location in project | Same folder as `manage.py` |
| Bound to | Client's hard disk serial number or MAC address |
| Has expiry | Yes — set when generating |
| Transferable | ❌ No — works only on bound machine |

---

## Client License Record

Keep a record of all client licenses:

| Client ID | Client Name | Machine Serial | License File | Expiry | Generated On |
|---|---|---|---|---|---|
| client001 | ABC Company | BLH2-3924 | licenses/client001/license.lic | 2027-12-31 | 2026-03-14 |
| client002 | XYZ Pvt Ltd | KLM4-5678 | licenses/client002/license.lic | 2027-12-31 | 2026-03-14 |

---

## Generate New Client License

### Step 1 — Get Client Machine ID

Run this on **client's machine**:
```bash
pip install pyarmor==7.7.4
pyarmor hdinfo
```

Note down:
```
Default Harddisk Serial Number: 'xxxx-xxxx'   ← use this
Default Mac address: 'xx:xx:xx:xx:xx:xx'
```

### Step 2 — Generate License on YOUR Machine

```bash
cd d:\your-project\

# Using Hard disk serial (recommended)
pyarmor licenses --expired 2027-12-31 --bind-disk "CLIENT_DISK_SERIAL" client001

# OR using MAC address
pyarmor licenses --expired 2027-12-31 --bind-mac "CLIENT_MAC_ADDRESS" client001
```

### Step 3 — Place in dist/ and Send

```bash
copy licenses\client001\license.lic dist\
powershell Compress-Archive -Path dist\* -DestinationPath EMB-255MT-client001.zip
```

---

## Renew Expired License

When client's license expires:

```bash
# Generate new license with updated expiry date
pyarmor licenses --expired 2028-12-31 --bind-disk "SAME_CLIENT_DISK_SERIAL" client001-renewed

# Copy to dist/
copy licenses\client001-renewed\license.lic dist\

# ZIP and send to client
powershell Compress-Archive -Path dist\* -DestinationPath EMB-255MT-client001-renewed.zip
```

> ✅ Client just replaces the old `license.lic` with the new one — no need to reinstall anything.

---

## Client Moved to New Machine

If client replaces their PC or changes hard disk:

```bash
# Step 1 — Get NEW machine ID from client
pyarmor hdinfo  # run on new machine

# Step 2 — Generate new license for new machine
pyarmor licenses --expired 2027-12-31 --bind-disk "NEW_MACHINE_SERIAL" client001-newpc

# Step 3 — Send new license
copy licenses\client001-newpc\license.lic dist\
```

> ⚠️ Old license will NOT work on new machine — always regenerate.

---

## License Folder Structure

```
your-project/
  └── licenses/
        ├── client001/
        │     └── license.lic
        ├── client002/
        │     └── license.lic
        ├── client001-renewed/
        │     └── license.lic
        └── devtest/
              └── license.lic    ← your machine for testing
```

---

## Generate Test License for YOUR Machine

```bash
# Get your own machine ID
pyarmor hdinfo

# Generate license for your machine
pyarmor licenses --expired 2027-12-31 --bind-disk "YOUR_DISK_SERIAL" devtest

# Use for local testing
copy licenses\devtest\license.lic dist\
```
# How to Make It Even Stronger
## Bind license to BOTH disk serial AND MAC address:

```bash
pyarmor licenses \
  --expired 2027-12-31 \
  --bind-disk "CLIENT_DISK_SERIAL" \
  --bind-mac "CLIENT_MAC_ADDRESS" \
  client001
```

---

## Important Rules

- ✅ Each client gets a **unique** license file
- ✅ One license = one machine only
- ✅ Always update client record table when generating new license
- ✅ Keep all licenses/ folder backed up safely
- ❌ Never send one client's license to another client
- ❌ Never delete old license files — keep them for reference
- ❌ Never share your master pyarmor setup with anyone

---

*License Management Guide — EMB-255MT*
*PyArmor 7.7.4 | Windows*
