# encrypt.py
import os
import sys
import shutil
import subprocess

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DIST_DIR     = os.path.join(PROJECT_ROOT, "dist")

# ============================================================
# CONFIG
# ============================================================
SKIP_FOLDERS = {
    "venv", "venv310", ".git", "__pycache__", "dist",
    "licenses", "security", "static", "templates",
    "migrations", "node_modules", ".pyarmor"
}

SKIP_FILES = {
    "encrypt.py", "check_form_data.py", "check_master_temp.py",
    "redefine_table.py", "test_save_flow.py"
}

COPY_EXTENSIONS = {
    ".html", ".css", ".js", ".png", ".jpg", ".jpeg",
    ".ico", ".svg", ".gif", ".mp4", ".woff", ".woff2",
    ".ttf", ".eot", ".txt", ".bat", ".env",
    ".json", ".xml", ".csv"
}

COPY_ROOT_FILES = {
    "requirements.txt", "FP-80MT.bat", ".env",
    "tssx-icon (1).ico", "Dump20260226.sql"
}
# ============================================================


def log(msg, level="INFO"):
    icons = {"INFO": "→", "OK": "✅", "SKIP": "⏭ ", "ERR": "❌"}
    print(f"  {icons.get(level, '•')} {msg}")


def clean_dist():
    if os.path.exists(DIST_DIR):
        log("Cleaning old dist/ folder...", "INFO")
        shutil.rmtree(DIST_DIR)
    os.makedirs(DIST_DIR)
    log("Fresh dist/ created", "OK")


def find_top_level_packages(root):
    """
    Find ONLY top-level Django packages.
    Skips subpackages — --recursive handles them automatically.
    Example: finds flowserve_app/ and flowserve_soft/
             skips flowserve_app/views/, flowserve_app/urls/ etc.
    """
    top_level = []

    for item in os.listdir(root):
        # Skip unwanted folders
        if item in SKIP_FOLDERS or item.startswith("."):
            continue

        full_path = os.path.join(root, item)

        # Only folders with __init__.py
        if os.path.isdir(full_path):
            init_file = os.path.join(full_path, "__init__.py")
            if os.path.exists(init_file):
                top_level.append((full_path, item))
                log(f"Found package: {item}/", "OK")

    return top_level


def encrypt_package(source_path, rel_path):
    """Encrypt a top-level package recursively"""

    init_file    = os.path.join(source_path, "__init__.py")
    output_path  = os.path.join(DIST_DIR, rel_path)

    init_file_fwd   = init_file.replace("\\", "/")
    output_path_fwd = output_path.replace("\\", "/")

    log(f"Encrypting: {rel_path}/ (including all subfolders)", "INFO")

    result = subprocess.run(
        [
            sys.executable, "-m", "pyarmor.pyarmor",
            "obfuscate",
            "--recursive",
            "--output", output_path_fwd,
            init_file_fwd
        ],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        log(f"FAILED: {rel_path}", "ERR")
        print(result.stderr[-500:])
        return False

    log(f"Done: {rel_path}/", "OK")
    return True


def encrypt_manage():
    """Encrypt manage.py"""
    manage_src = os.path.join(PROJECT_ROOT, "manage.py")
    if not os.path.exists(manage_src):
        log("manage.py not found — skipping", "SKIP")
        return

    log("Encrypting: manage.py", "INFO")

    result = subprocess.run(
        [
            sys.executable, "-m", "pyarmor.pyarmor",
            "obfuscate",
            "--output", DIST_DIR,
            manage_src
        ],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        log("FAILED: manage.py", "ERR")
        print(result.stderr[-500:])
    else:
        log("Done: manage.py", "OK")


def copy_non_python_files(root):
    """Copy static, templates, media files maintaining folder structure"""
    log("Copying static/template/media files...", "INFO")
    copied = 0

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [
            d for d in dirnames
            if d not in SKIP_FOLDERS and not d.startswith(".")
        ]

        for filename in filenames:
            ext = os.path.splitext(filename)[1].lower()
            if ext in COPY_EXTENSIONS:
                src  = os.path.join(dirpath, filename)
                rel  = os.path.relpath(src, root)
                dest = os.path.join(DIST_DIR, rel)
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                shutil.copy2(src, dest)
                copied += 1

    log(f"Copied {copied} static/template files", "OK")


def copy_root_files():
    """Copy root level files into dist/"""
    log("Copying root files...", "INFO")
    for filename in COPY_ROOT_FILES:
        src = os.path.join(PROJECT_ROOT, filename)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(DIST_DIR, filename))
            log(f"Copied: {filename}", "OK")
        else:
            log(f"Not found (skipped): {filename}", "SKIP")


def check_pyarmor():
    result = subprocess.run(
        [sys.executable, "-m", "pyarmor.pyarmor", "--version"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        log("PyArmor not installed! Run: pip install pyarmor==7.7.4", "ERR")
        sys.exit(1)
    log(f"PyArmor: {result.stdout.strip().split(chr(10))[0]}", "OK")


def print_header():
    print()
    print("  " + "=" * 56)
    print("    Django PyArmor Auto Encryption Script")
    print(f"    Project: {os.path.basename(PROJECT_ROOT)}")
    print("  " + "=" * 56)
    print()


def print_summary(packages, failed):
    print()
    print("  " + "=" * 56)
    if not failed:
        print(f"    ✅ Encryption Complete — 0 failures")
    else:
        print(f"    ⚠️  Completed with {len(failed)} failure(s)")
        for f in failed:
            print(f"       ❌ {f}")
    print(f"    📦 Packages encrypted : {len(packages) - len(failed)}")
    print(f"    📁 Output folder      : dist/")
    print()
    print("    ⚠️  Next Steps:")
    print("    1. Copy license into dist/:")
    print("       pyarmor licenses --expired 2027-12-31 --bind-disk 'ID' client001")
    print("       copy licenses\\client001\\license.lic dist\\")
    print()
    print("    2. Test:")
    print("       cd dist && python manage.py runserver")
    print()
    print("    3. ZIP for client:")
    print("       powershell Compress-Archive -Path dist\\* -DestinationPath client.zip")
    print("  " + "=" * 56)
    print()


def main():
    print_header()
    check_pyarmor()
    clean_dist()

    # Find ONLY top-level packages
    log("Scanning for top-level packages only...", "INFO")
    packages = find_top_level_packages(PROJECT_ROOT)
    log(f"Found {len(packages)} top-level packages", "OK")
    print()

    # Encrypt each top-level package (--recursive handles subfolders)
    failed = []
    for source_path, rel_path in packages:
        success = encrypt_package(source_path, rel_path)
        if not success:
            failed.append(rel_path)

    print()

    # Encrypt manage.py
    encrypt_manage()
    print()

    # Copy static/templates
    copy_non_python_files(PROJECT_ROOT)

    # Copy root files
    copy_root_files()

    print_summary(packages, failed)


if __name__ == "__main__":
    main()