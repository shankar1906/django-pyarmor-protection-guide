# PyArmor Security & License Flow Guide
> How PyArmor protects your Django project — flow diagrams, security levels, and key concepts explained clearly.

---

## 1. Overall Protection Flow

```
┌─────────────────────────────────────────────────────────────┐
│                      YOUR MACHINE                           │
│                                                             │
│   Original Source Code                                      │
│          ↓                                                  │
│   pyarmor init → Creates .pyarmor/pyarmor.key               │
│          ↓              (YOUR private master key)           │
│   PyArmor Encrypts Code using AES-256                       │
│          ↓                                                  │
│   dist/ folder created (encrypted binary)                   │
│          ↓                                                  │
│   License generated & signed with YOUR private key          │
│          ↓                                                  │
│   ZIP sent to client ──────────────────────────────────►   │
└─────────────────────────────────────────────────────────────┘
                                                    │
                                                    ▼
┌─────────────────────────────────────────────────────────────┐
│                     CLIENT MACHINE                          │
│                                                             │
│   Receives dist/ + license.lic                              │
│          ↓                                                  │
│   pytransform runtime checks license                        │
│          ↓                                                  │
│   ┌──────────────────────────────────┐                      │
│   │  License valid + correct machine?│                      │
│   └──────────────────────────────────┘                      │
│          ↓                    ↓                             │
│         YES                   NO                            │
│          ↓                    ↓                             │
│   ✅ App Starts          ❌ App Rejected                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. How the Private Key Works

```
┌─────────────────────────────────────────────────────────────┐
│                    KEY GENERATION                           │
│                                                             │
│   YOUR Machine                                              │
│   ─────────────                                             │
│   pyarmor init                                              │
│          ↓                                                  │
│   .pyarmor/pyarmor.key  ←── YOUR unique private key        │
│          │                   (never leaves your machine)    │
│          │                                                  │
│          ├──► Used to ENCRYPT your source code              │
│          │                                                  │
│          └──► Used to SIGN every license.lic you generate   │
│                                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   LICENSE VERIFICATION                      │
│                                                             │
│   Client runs → python manage.py runserver                  │
│          ↓                                                  │
│   pytransform reads license.lic                             │
│          ↓                                                  │
│   Checks: Is this signed with the CORRECT private key?      │
│          ↓                    ↓                             │
│         YES                   NO                            │
│   (matches your key)    (attacker's key)                    │
│          ↓                    ↓                             │
│   ✅ Accepted           ❌ Rejected immediately             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. License Binding Flow

```
                    DEVELOPER MACHINE
                    ─────────────────

        Get Client Hardware Info
               ↓
    ┌──────────────────────┐
    │  Harddisk Serial No. │  ← from pyarmor hdinfo
    │  MAC Address         │    (run on client PC)
    └──────────────────────┘
               ↓
    Generate License bound to that hardware
               ↓
    license.lic  ←── Signed with YOUR private key
                      + Locked to CLIENT hardware
               ↓
    Send to client


                    CLIENT MACHINE
                    ──────────────

    Receives license.lic
               ↓
    pytransform checks 3 things:
               ↓
    ┌─────────────────────────────────────┐
    │ 1. Is signature from correct key?   │
    │ 2. Is this the correct machine?     │
    │ 3. Is license still valid (expiry)? │
    └─────────────────────────────────────┘
               ↓                    ↓
          ALL 3 PASS            ANY 1 FAILS
               ↓                    ↓
        ✅ App runs           ❌ App blocked
```

---

## 4. What Happens If Attacker Tries to Fake a License

```
    ATTACKER MACHINE
    ─────────────────────────────────────────────────

    Attacker installs PyArmor
               ↓
    pyarmor init on their machine
               ↓
    Creates their own .pyarmor/pyarmor.key
    (DIFFERENT from your key)
               ↓
    Tries to generate a license
               ↓
    license.lic signed with ATTACKER key
               ↓
    Copies to your encrypted dist/
               ↓
    pytransform checks signature
               ↓
    ❌ SIGNATURE MISMATCH — REJECTED
       App will NOT start


    WHY? Because your encrypted code only
    accepts licenses signed with YOUR key.
    Attacker's key = always wrong = always rejected.
```

---

## 5. Multi-Client License Flow

```
                        YOUR MACHINE
                        ─────────────

    Same encrypted dist/ for all clients
              │
              ├──────────────────────────────────────────┐
              │                                          │
              ▼                                          ▼
    Client A Machine                          Client B Machine
    ─────────────────                         ─────────────────
    Disk Serial: AAA-111                      Disk Serial: BBB-222
    MAC: aa:bb:cc:dd                          MAC: ee:ff:gg:hh
              │                                          │
              ▼                                          ▼
    license.lic (for A)                       license.lic (for B)
    Bound to AAA-111                          Bound to BBB-222
              │                                          │
              ▼                                          ▼
    ✅ Runs on A only                         ✅ Runs on B only


    ❌ Client A's license on Client B's machine → REJECTED
    ❌ Client B's license on Client A's machine → REJECTED
```

---

## 6. What Each Party Can and Cannot Do

```
┌──────────────────────────────────────────────────────────────┐
│                        YOU (Developer)                       │
├──────────────────────────────────────────────────────────────┤
│  ✅ Encrypt source code                                      │
│  ✅ Generate licenses for any client                         │
│  ✅ Set expiry dates                                         │
│  ✅ Revoke access (don't renew license)                      │
│  ✅ Bind to specific hardware                                │
│  ✅ See original source code                                 │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                     CLIENT (Legitimate)                      │
├──────────────────────────────────────────────────────────────┤
│  ✅ Run the software on their machine                        │
│  ✅ Use all features normally                                │
│  ❌ Cannot read source code                                  │
│  ❌ Cannot copy to another machine                           │
│  ❌ Cannot generate their own license                        │
│  ❌ Cannot share license with others                         │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                     ATTACKER                                 │
├──────────────────────────────────────────────────────────────┤
│  ❌ Cannot read encrypted source code                        │
│  ❌ Cannot generate a valid license                          │
│  ❌ Cannot run on unauthorized machine                       │
│  ❌ Cannot use AI to decode encrypted binary                 │
│  ❌ Cannot transfer license between machines                 │
│  ❌ Cannot use after expiry                                  │
└──────────────────────────────────────────────────────────────┘
```

---

## 7. Security Layers

```
Layer 1 — Source Code Encryption
─────────────────────────────────
  Original .py → AES-256 encrypted binary
  No variable names, no logic visible
  Result: Source is completely unreadable

          ↓

Layer 2 — License Signature Verification
─────────────────────────────────────────
  Every license signed with your private key
  Fake licenses rejected immediately
  Result: Nobody can generate a valid license

          ↓

Layer 3 — Hardware Binding
───────────────────────────
  License locked to specific disk serial + MAC
  Copied license won't work on different machine
  Result: Software runs on ONE machine only

          ↓

Layer 4 — Expiry Control
─────────────────────────
  License has expiry date
  After expiry → software stops working
  Result: You control how long client can use it

          ↓

Layer 5 — Runtime Protection
─────────────────────────────
  pytransform validates all checks at startup
  No checks pass = no startup at all
  Result: Zero chance of bypassing protection
```

---

## 8. Real World Threat Analysis

```
┌────────────────────────────────────────────────────────────┐
│  THREAT                    │  RISK    │  REASON            │
├────────────────────────────────────────────────────────────┤
│  Read source code          │ 🟢 None  │ AES-256 encrypted  │
│  Fake a license            │ 🟢 None  │ Needs your key     │
│  Copy to another machine   │ 🟢 None  │ Hardware bound     │
│  Use after expiry          │ 🟢 None  │ Date check         │
│  AI decoding               │ 🟢 None  │ Binary = unreadable│
│  Share license between PCs │ 🟢 None  │ Hardware mismatch  │
│  Casual reverse engineer   │ 🟢 None  │ Nothing to read    │
│  Expert reverse engineer   │ 🟡 Low   │ Months of effort   │
│  Your team leaking source  │ 🔴 High  │ Human risk         │
│  Losing .pyarmor/ folder   │ 🔴 High  │ Can't make licenses│
│  Losing original source    │ 🔴 High  │ Cannot recover     │
└────────────────────────────────────────────────────────────┘
```

---

## 9. The Golden Rules

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   🔐 NEVER share .pyarmor/ folder with anyone              │
│      → This is your master key                             │
│                                                             │
│   🔐 NEVER share original source code                      │
│      → Once shared, protection is useless                  │
│                                                             │
│   🔐 ALWAYS keep 3 backups of original source              │
│      → Git private repo + local ZIP + external drive       │
│                                                             │
│   🔐 ALWAYS bind license to hardware                       │
│      → Never generate license without --bind-disk          │
│                                                             │
│   🔐 ALWAYS set expiry dates on licenses                   │
│      → Gives you control over client access                │
│                                                             │
│   🔐 NEVER send same license to two clients                │
│      → Each client gets unique license                     │
│                                                             │
│   🔐 NEVER push dist/ or .pyarmor/ to public git           │
│      → Keep repo private always                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 10. License Lifecycle

```
    New Client Request
           ↓
    Get hardware ID from client
           ↓
    Generate license (bound + expiry)
           ↓
    Send dist/ + license.lic
           ↓
    Client uses software
           ↓
    ┌──────────────────────┐
    │  License expired?    │
    └──────────────────────┘
           ↓          ↓
          YES          NO
           ↓          ↓
    Client contacts   Software
    you for renewal   continues
           ↓
    Generate new license
    with updated expiry
           ↓
    Send only license.lic
    (no need to resend full ZIP)
           ↓
    Client replaces old license.lic
           ↓
    Software works again ✅
```

---

*Security & License Flow Guide — EMB-255MT*
*PyArmor 7.7.4 | Python 3.10 | Windows*
