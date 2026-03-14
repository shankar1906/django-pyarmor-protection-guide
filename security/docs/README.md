# Django PyArmor Protection Guide

Complete guide to encrypt and protect a Django project using PyArmor 7.7.4 with machine-bound licensing for secure client deployment on Windows.

---

## Docs

| File | Description |
|---|---|
| [Pyarmor Protection Guide](./Pyarmor%20protection%20guide.md) | Full step-by-step encryption & deployment process |
| [Pyarmor Troubleshoot Guide](./Pyarmor%20troubleshoot%20guide%20.md) | All real-world errors and exact fixes |
| [Client Setup Guide](./Client-Setup-Guide.md) | Simple guide to give directly to client |
| [License Management](./License-Management.md) | How to manage licenses for multiple clients |
| [Release Checklist](./Release-Checklist.md) | Checklist before every client delivery |

---

## Stack

- Python 3.10
- Django
- PyArmor 7.7.4
- Windows

---

## Quick Summary

```
Developer Machine          Client Machine
──────────────────         ──────────────────
Encrypt with PyArmor  →    Receives ZIP
Get client machine ID ←    Sends machine ID
Generate license      →    Receives license
                           Runs software ✅
```

---

> ⚠️ Keep this repo **Private** — contains client protection strategy.
