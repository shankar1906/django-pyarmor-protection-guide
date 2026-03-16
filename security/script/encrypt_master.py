"""
╔══════════════════════════════════════════════════════════════════╗
║         MASTER PYARMOR ENCRYPTION SCRIPT                        ║
║         Works with ANY Django Project Structure                  ║
║         Version: 2.0.0                                          ║
║         Author : Teslead                                        ║
╚══════════════════════════════════════════════════════════════════╝

USAGE:
    python encrypt_master.py                  ← interactive mode
    python encrypt_master.py --auto           ← auto detect all settings
    python encrypt_master.py --help           ← show help
"""

import os
import sys
import json
import shutil
import subprocess
import argparse
from pathlib import Path
from datetime import datetime


# ══════════════════════════════════════════════════════════════════
#  COLORS
# ══════════════════════════════════════════════════════════════════

class C:
    RED    = "\033[91m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    BLUE   = "\033[94m"
    CYAN   = "\033[96m"
    WHITE  = "\033[97m"
    BOLD   = "\033[1m"
    RESET  = "\033[0m"


# ══════════════════════════════════════════════════════════════════
#  LOGGER
# ══════════════════════════════════════════════════════════════════

def log(msg, level="INFO"):
    icons = {
        "INFO"  : f"{C.CYAN}→{C.RESET}",
        "OK"    : f"{C.GREEN}✅{C.RESET}",
        "SKIP"  : f"{C.YELLOW}⏭ {C.RESET}",
        "ERR"   : f"{C.RED}❌{C.RESET}",
        "WARN"  : f"{C.YELLOW}⚠️ {C.RESET}",
        "HEAD"  : f"{C.BOLD}{C.BLUE}►{C.RESET}",
        "INPUT" : f"{C.CYAN}✎{C.RESET}",
    }
    print(f"  {icons.get(level, '•')} {msg}")


def header(title):
    print()
    print(f"  {C.BOLD}{C.BLUE}{'═' * 56}{C.RESET}")
    print(f"  {C.BOLD}{C.WHITE}  {title}{C.RESET}")
    print(f"  {C.BOLD}{C.BLUE}{'═' * 56}{C.RESET}")
    print()


def divider():
    print(f"  {C.BLUE}{'─' * 56}{C.RESET}")


def ask(prompt, default=None, required=True):
    """Ask user for input with optional default"""
    if default:
        display = f"{C.CYAN}{prompt}{C.RESET} [{C.YELLOW}{default}{C.RESET}]: "
    else:
        display = f"{C.CYAN}{prompt}{C.RESET}: "

    while True:
        val = input(f"  {display}").strip()
        if not val and default is not None:
            return default
        if val:
            return val
        if not required:
            return ""
        print(f"  {C.RED}  ✗ This field is required.{C.RESET}")


def ask_yes_no(prompt, default="y"):
    """Ask yes/no question"""
    options = "[Y/n]" if default == "y" else "[y/N]"
    val = input(f"  {C.CYAN}{prompt}{C.RESET} {options}: ").strip().lower()
    if not val:
        return default == "y"
    return val in ("y", "yes")


def ask_choice(prompt, choices, default=None):
    """Ask user to pick from a numbered list"""
    print(f"  {C.CYAN}{prompt}{C.RESET}")
    for i, choice in enumerate(choices, 1):
        marker = f"{C.YELLOW}(default){C.RESET}" if choice == default else ""
        print(f"    {C.BOLD}{i}.{C.RESET} {choice} {marker}")

    while True:
        val = input(f"  {C.CYAN}  Enter number{C.RESET}: ").strip()
        if not val and default:
            return default
        try:
            idx = int(val) - 1
            if 0 <= idx < len(choices):
                return choices[idx]
        except ValueError:
            pass
        print(f"  {C.RED}  ✗ Invalid choice.{C.RESET}")


# ══════════════════════════════════════════════════════════════════
#  AUTO DETECTOR
# ══════════════════════════════════════════════════════════════════

def find_manage_py(root):
    """Search for manage.py recursively"""
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in {
            "venv", "venv310", ".git", "__pycache__", "dist",
            "node_modules", ".pyarmor", "venv311", "env"
        }]
        if "manage.py" in filenames:
            return dirpath
    return None


def find_django_packages(root, skip_folders):
    """Find all top-level Django packages (folders with __init__.py)"""
    packages = []
    for item in os.listdir(root):
        if item in skip_folders or item.startswith("."):
            continue
        full_path = os.path.join(root, item)
        if os.path.isdir(full_path):
            if os.path.exists(os.path.join(full_path, "__init__.py")):
                packages.append((full_path, item))
    return packages


def find_venv(root):
    """Find virtual environment in project"""
    common_venv_names = [
        "venv", "venv310", "venv311", ".venv", "env",
        "virtualenv", ".virtualenv"
    ]
    outer = os.path.dirname(root)
    for loc in [root, outer]:
        for name in common_venv_names:
            path = os.path.join(loc, name)
            if os.path.isdir(path):
                return name, path
    return None, None


def find_root_files(root):
    """Detect important root files to copy"""
    important = [
        "requirements.txt", ".env", "manage.py",
        "FP-80MT.bat", "*.ico", "*.sql", "*.bat",
        "Procfile", "runtime.txt"
    ]
    found = []
    for f in os.listdir(root):
        if f in important:
            found.append(f)
        elif f.endswith((".ico", ".bat", ".sql")) and os.path.isfile(os.path.join(root, f)):
            found.append(f)
    return found


def detect_project_structure(start_path):
    """Auto detect Django project structure"""
    log("Scanning project structure...", "INFO")

    manage_dir = find_manage_py(start_path)
    if not manage_dir:
        log("manage.py not found — please enter path manually", "WARN")
        return None

    log(f"Found manage.py at: {manage_dir}", "OK")
    return manage_dir


def check_pyarmor():
    """Check PyArmor version"""
    result = subprocess.run(
        [sys.executable, "-m", "pyarmor.pyarmor", "--version"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        return False, None
    version = result.stdout.strip().split("\n")[0]
    return True, version


# ══════════════════════════════════════════════════════════════════
#  ENCRYPTION ENGINE
# ══════════════════════════════════════════════════════════════════

def clean_dist(dist_dir):
    if os.path.exists(dist_dir):
        log("Cleaning old dist/ folder...", "INFO")
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir)
    log("Fresh dist/ created", "OK")


def encrypt_package(source_path, rel_path, dist_dir):
    init_file       = os.path.join(source_path, "__init__.py")
    output_path     = os.path.join(dist_dir, rel_path)
    init_file_fwd   = init_file.replace("\\", "/")
    output_path_fwd = output_path.replace("\\", "/")

    log(f"Encrypting: {rel_path}/ (recursive)", "INFO")

    result = subprocess.run(
        [
            sys.executable, "-m", "pyarmor.pyarmor",
            "obfuscate", "--recursive",
            "--output", output_path_fwd,
            init_file_fwd
        ],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        log(f"FAILED: {rel_path}", "ERR")
        err = result.stderr
        if "Too big code object" in err:
            log("File too large for trial version — needs PyArmor paid license", "WARN")
        else:
            print(err[-300:])
        return False

    log(f"Done: {rel_path}/", "OK")
    return True


def encrypt_manage(project_root, dist_dir):
    manage_src = os.path.join(project_root, "manage.py")
    if not os.path.exists(manage_src):
        log("manage.py not found — skipping", "SKIP")
        return

    log("Encrypting: manage.py", "INFO")
    result = subprocess.run(
        [
            sys.executable, "-m", "pyarmor.pyarmor",
            "obfuscate", "--output", dist_dir, manage_src
        ],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        log("FAILED: manage.py", "ERR")
        print(result.stderr[-300:])
    else:
        log("Done: manage.py", "OK")


def copy_non_python_files(project_root, dist_dir, skip_folders, copy_extensions):
    log("Copying static/template/media files...", "INFO")
    copied = 0

    for dirpath, dirnames, filenames in os.walk(project_root):
        dirnames[:] = [
            d for d in dirnames
            if d not in skip_folders and not d.startswith(".")
        ]
        for filename in filenames:
            ext = os.path.splitext(filename)[1].lower()
            if ext in copy_extensions:
                src  = os.path.join(dirpath, filename)
                rel  = os.path.relpath(src, project_root)
                dest = os.path.join(dist_dir, rel)
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                shutil.copy2(src, dest)
                copied += 1

    log(f"Copied {copied} static/template/media files", "OK")


def copy_root_files(project_root, dist_dir, root_files):
    log("Copying root files...", "INFO")
    for filename in root_files:
        src = os.path.join(project_root, filename)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(dist_dir, filename))
            log(f"Copied: {filename}", "OK")
        else:
            log(f"Not found (skipped): {filename}", "SKIP")


def generate_license(project_root, dist_dir, config):
    """Generate PyArmor license based on config"""
    if not config.get("generate_license"):
        return

    license_name    = config.get("license_name", "client001")
    expiry          = config.get("expiry", "2027-12-31")
    bind_disk       = config.get("bind_disk", "")
    bind_mac        = config.get("bind_mac", "")

    cmd = [
        sys.executable, "-m", "pyarmor.pyarmor",
        "licenses",
        f"--expired", expiry,
    ]

    if bind_disk:
        cmd += ["--bind-disk", bind_disk]
    if bind_mac:
        cmd += ["--bind-mac", bind_mac]

    cmd.append(license_name)

    log(f"Generating license: {license_name} (expires: {expiry})", "INFO")

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=project_root)

    if result.returncode != 0:
        log("License generation failed", "ERR")
        print(result.stderr[-300:])
        return

    license_src  = os.path.join(project_root, "licenses", license_name, "license.lic")
    license_dest = os.path.join(dist_dir, "license.lic")

    if os.path.exists(license_src):
        shutil.copy2(license_src, license_dest)
        log(f"License copied to dist/license.lic", "OK")
    else:
        log(f"License file not found at: {license_src}", "WARN")


def zip_dist(dist_dir, project_name):
    """Create ZIP of dist/ folder"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_name  = f"{project_name}-client-{timestamp}.zip"
    zip_path  = os.path.join(os.path.dirname(dist_dir), zip_name)

    log(f"Creating ZIP: {zip_name}", "INFO")

    result = subprocess.run(
        ["powershell", "Compress-Archive",
         "-Path", os.path.join(dist_dir, "*"),
         "-DestinationPath", zip_path,
         "-Force"],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        # Fallback: Python zip
        import zipfile
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(dist_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname   = os.path.relpath(file_path, dist_dir)
                    zf.write(file_path, arcname)

    if os.path.exists(zip_path):
        size_mb = os.path.getsize(zip_path) / (1024 * 1024)
        log(f"ZIP created: {zip_name} ({size_mb:.1f} MB)", "OK")
        return zip_path
    else:
        log("ZIP creation failed", "ERR")
        return None


def save_config(config, config_path):
    """Save config to JSON for reuse"""
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    log(f"Config saved: {os.path.basename(config_path)}", "OK")


def load_config(config_path):
    """Load saved config"""
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return json.load(f)
    return None


# ══════════════════════════════════════════════════════════════════
#  INTERACTIVE SETUP
# ══════════════════════════════════════════════════════════════════

def interactive_setup(start_path, auto=False):
    """Full interactive configuration wizard"""

    header("STEP 1 — Project Detection")

    # ── Detect project root ──────────────────────────────────────
    detected_root = detect_project_structure(start_path)

    if auto and detected_root:
        project_root = detected_root
        log(f"Auto-selected: {project_root}", "OK")
    else:
        project_root = ask(
            "Enter Django project root (where manage.py is)",
            default=detected_root or start_path
        )

    if not os.path.exists(os.path.join(project_root, "manage.py")):
        log("manage.py not found at that path!", "ERR")
        sys.exit(1)

    project_name = os.path.basename(project_root)
    log(f"Project: {project_name}", "OK")

    # ── Dist output path ─────────────────────────────────────────
    default_dist = os.path.join(os.path.dirname(project_root), "dist")
    if auto:
        dist_dir = default_dist
    else:
        dist_dir = ask("Output dist/ folder path", default=default_dist)

    # ── Find packages ────────────────────────────────────────────
    header("STEP 2 — Package Detection")

    default_skip = {
        "venv", "venv310", "venv311", ".venv", "env",
        ".git", "__pycache__", "dist", "licenses",
        "static", "templates", "migrations",
        "node_modules", ".pyarmor", "security"
    }

    log("Detected Django packages:", "INFO")
    packages = find_django_packages(project_root, default_skip)

    if not packages:
        log("No packages found!", "ERR")
        sys.exit(1)

    for _, name in packages:
        log(f"  {name}/", "OK")

    if not auto:
        extra = ask(
            "Add extra folders to SKIP (comma separated, or press Enter to skip)",
            default="", required=False
        )
        if extra:
            for folder in extra.split(","):
                default_skip.add(folder.strip())

    # ── Root files to copy ───────────────────────────────────────
    header("STEP 3 — Root Files")

    detected_files = find_root_files(project_root)
    log(f"Detected root files: {', '.join(detected_files) if detected_files else 'none'}", "INFO")

    if auto:
        root_files = set(detected_files)
    else:
        extra_files = ask(
            "Add extra files to copy to dist/ (comma separated, or Enter to skip)",
            default="", required=False
        )
        root_files = set(detected_files)
        if extra_files:
            for f in extra_files.split(","):
                root_files.add(f.strip())

    # ── License generation ───────────────────────────────────────
    header("STEP 4 — License Configuration")

    generate_license_flag = False
    bind_disk = bind_mac = expiry = license_name = ""

    if auto:
        generate_license_flag = False
        log("License generation skipped in auto mode", "SKIP")
        log("Run script again after getting client machine ID", "INFO")
    else:
        generate_license_flag = ask_yes_no(
            "Do you want to generate a machine-bound license now?", default="n"
        )

        if generate_license_flag:
            log("Run this on client machine to get hardware ID:", "INFO")
            log("  pyarmor hdinfo", "INFO")
            print()

            bind_type = ask_choice(
                "Bind license to:",
                ["Hard Disk Serial", "MAC Address", "Both", "No binding (test only)"],
                default="Hard Disk Serial"
            )

            if "Hard Disk" in bind_type or "Both" in bind_type:
                bind_disk = ask("Enter client Hard Disk Serial (e.g. BLH2-3924)")
            if "MAC" in bind_type or "Both" in bind_type:
                bind_mac = ask("Enter client MAC Address (e.g. f8:75:a4:xx:xx:xx)")

            expiry       = ask("License expiry date", default="2027-12-31")
            license_name = ask("License name (for your records)", default="client001")

    # ── ZIP after encryption ─────────────────────────────────────
    header("STEP 5 — Output Options")

    if auto:
        create_zip = True
    else:
        create_zip = ask_yes_no("Create ZIP file after encryption?", default="y")

    # ── Summary before run ───────────────────────────────────────
    header("CONFIGURATION SUMMARY")

    print(f"  {'Project Root':<22}: {C.WHITE}{project_root}{C.RESET}")
    print(f"  {'Project Name':<22}: {C.WHITE}{project_name}{C.RESET}")
    print(f"  {'Output (dist/)':<22}: {C.WHITE}{dist_dir}{C.RESET}")
    print(f"  {'Packages':<22}: {C.WHITE}{', '.join(n for _, n in packages)}{C.RESET}")
    print(f"  {'Skip Folders':<22}: {C.YELLOW}{', '.join(sorted(default_skip))}{C.RESET}")
    print(f"  {'Root Files':<22}: {C.WHITE}{', '.join(sorted(root_files)) if root_files else 'none'}{C.RESET}")
    print(f"  {'Generate License':<22}: {C.GREEN if generate_license_flag else C.YELLOW}{'Yes' if generate_license_flag else 'No'}{C.RESET}")
    if generate_license_flag:
        print(f"  {'License Name':<22}: {C.WHITE}{license_name}{C.RESET}")
        print(f"  {'Expiry':<22}: {C.WHITE}{expiry}{C.RESET}")
        if bind_disk:
            print(f"  {'Bind Disk':<22}: {C.WHITE}{bind_disk}{C.RESET}")
        if bind_mac:
            print(f"  {'Bind MAC':<22}: {C.WHITE}{bind_mac}{C.RESET}")
    print(f"  {'Create ZIP':<22}: {C.GREEN if create_zip else C.YELLOW}{'Yes' if create_zip else 'No'}{C.RESET}")
    print()

    if not auto:
        if not ask_yes_no("Proceed with encryption?", default="y"):
            log("Cancelled.", "WARN")
            sys.exit(0)

    return {
        "project_root"      : project_root,
        "project_name"      : project_name,
        "dist_dir"          : dist_dir,
        "packages"          : packages,
        "skip_folders"      : default_skip,
        "root_files"        : root_files,
        "generate_license"  : generate_license_flag,
        "license_name"      : license_name,
        "expiry"            : expiry,
        "bind_disk"         : bind_disk,
        "bind_mac"          : bind_mac,
        "create_zip"        : create_zip,
        "copy_extensions"   : {
            ".html", ".css", ".js", ".png", ".jpg", ".jpeg",
            ".ico", ".svg", ".gif", ".mp4", ".woff", ".woff2",
            ".ttf", ".eot", ".txt", ".bat", ".env",
            ".json", ".xml", ".csv", ".md", ".pdf"
        }
    }


# ══════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════

def print_banner():
    print()
    print(f"  {C.BOLD}{C.BLUE}╔══════════════════════════════════════════════════════╗{C.RESET}")
    print(f"  {C.BOLD}{C.BLUE}║{C.RESET}  {C.BOLD}{C.WHITE}MASTER PYARMOR ENCRYPTION SCRIPT v2.0{C.RESET}              {C.BOLD}{C.BLUE}║{C.RESET}")
    print(f"  {C.BOLD}{C.BLUE}║{C.RESET}  {C.CYAN}Works with ANY Django Project Structure{C.RESET}          {C.BOLD}{C.BLUE}║{C.RESET}")
    print(f"  {C.BOLD}{C.BLUE}╚══════════════════════════════════════════════════════╝{C.RESET}")
    print()


def print_final_summary(config, failed, zip_path, start_time):
    elapsed = (datetime.now() - start_time).seconds
    total   = len(config["packages"])
    success = total - len(failed)

    print()
    print(f"  {C.BOLD}{C.BLUE}╔══════════════════════════════════════════════════════╗{C.RESET}")
    print(f"  {C.BOLD}{C.BLUE}║{C.RESET}  {C.BOLD}ENCRYPTION RESULTS{C.RESET}                                 {C.BOLD}{C.BLUE}║{C.RESET}")
    print(f"  {C.BOLD}{C.BLUE}╚══════════════════════════════════════════════════════╝{C.RESET}")
    print()
    print(f"  {'Status':<22}: {C.GREEN + '✅ SUCCESS' + C.RESET if not failed else C.RED + '⚠️  PARTIAL' + C.RESET}")
    print(f"  {'Packages encrypted':<22}: {C.WHITE}{success}/{total}{C.RESET}")
    print(f"  {'Time taken':<22}: {C.WHITE}{elapsed}s{C.RESET}")
    print(f"  {'Output folder':<22}: {C.WHITE}{config['dist_dir']}{C.RESET}")

    if zip_path:
        print(f"  {'ZIP file':<22}: {C.WHITE}{os.path.basename(zip_path)}{C.RESET}")

    if failed:
        print()
        print(f"  {C.RED}Failed packages:{C.RESET}")
        for f in failed:
            print(f"    {C.RED}❌ {f}{C.RESET}")
        print()
        print(f"  {C.YELLOW}⚠️  If failure is 'Too big code object' → you need PyArmor paid license{C.RESET}")
        print(f"  {C.YELLOW}   Purchase at: https://pyarmor.readthedocs.io/en/latest/licenses.html{C.RESET}")

    print()
    print(f"  {C.BOLD}Next Steps:{C.RESET}")

    if not config.get("generate_license"):
        print(f"  {C.CYAN}1.{C.RESET} Get client machine ID:")
        print(f"     {C.WHITE}pyarmor hdinfo{C.RESET}  (run on client PC)")
        print()
        print(f"  {C.CYAN}2.{C.RESET} Generate license:")
        print(f"     {C.WHITE}pyarmor licenses --expired 2027-12-31 --bind-disk 'ID' client001{C.RESET}")
        print(f"     {C.WHITE}copy licenses\\client001\\license.lic dist\\{C.RESET}")
        print()
        print(f"  {C.CYAN}3.{C.RESET} Test encrypted project:")
        print(f"     {C.WHITE}cd dist && python manage.py runserver{C.RESET}")
        print()
        print(f"  {C.CYAN}4.{C.RESET} ZIP and send to client:")
        print(f"     {C.WHITE}powershell Compress-Archive -Path dist\\* -DestinationPath {config['project_name']}-client.zip{C.RESET}")
    else:
        print(f"  {C.CYAN}1.{C.RESET} Test encrypted project:")
        print(f"     {C.WHITE}cd dist && python manage.py runserver{C.RESET}")
        print()
        print(f"  {C.CYAN}2.{C.RESET} ZIP already created — send to client ✅")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Master PyArmor Encryption Script — Works with ANY Django project"
    )
    parser.add_argument(
        "--auto", action="store_true",
        help="Auto-detect all settings without prompts"
    )
    parser.add_argument(
        "--root", type=str, default=None,
        help="Override project root path manually"
    )
    parser.add_argument(
        "--config", type=str, default=None,
        help="Load saved config JSON file"
    )
    parser.add_argument(
        "--save-config", action="store_true",
        help="Save config to encrypt_config.json for reuse"
    )

    args       = parser.parse_args()
    start_path = args.root or os.path.dirname(os.path.abspath(__file__))
    start_time = datetime.now()

    print_banner()

    # ── Check PyArmor ───────────────────────────────────────────
    pyarmor_ok, pyarmor_ver = check_pyarmor()
    if not pyarmor_ok:
        log("PyArmor not installed!", "ERR")
        log("Run: pip install pyarmor==7.7.4", "INFO")
        sys.exit(1)
    log(f"PyArmor ready: {pyarmor_ver}", "OK")

    # ── Load saved config or run wizard ─────────────────────────
    config_path = os.path.join(start_path, "encrypt_config.json")

    if args.config and os.path.exists(args.config):
        log(f"Loading config: {args.config}", "INFO")
        config = load_config(args.config)
        config["packages"] = find_django_packages(
            config["project_root"], config["skip_folders"]
        )
    else:
        config = interactive_setup(start_path, auto=args.auto)

    # ── Save config if requested ─────────────────────────────────
    if args.save_config:
        serializable = {
            k: list(v) if isinstance(v, set) else v
            for k, v in config.items()
            if k != "packages"
        }
        save_config(serializable, config_path)

    # ── Run Encryption ───────────────────────────────────────────
    header("ENCRYPTING PROJECT")

    clean_dist(config["dist_dir"])

    failed = []
    for source_path, rel_path in config["packages"]:
        success = encrypt_package(source_path, rel_path, config["dist_dir"])
        if not success:
            failed.append(rel_path)

    print()
    encrypt_manage(config["project_root"], config["dist_dir"])
    print()

    copy_non_python_files(
        config["project_root"],
        config["dist_dir"],
        config["skip_folders"],
        config["copy_extensions"]
    )

    copy_root_files(
        config["project_root"],
        config["dist_dir"],
        config["root_files"]
    )

    # ── Generate License ─────────────────────────────────────────
    if config.get("generate_license"):
        print()
        header("GENERATING LICENSE")
        generate_license(config["project_root"], config["dist_dir"], config)

    # ── Create ZIP ───────────────────────────────────────────────
    zip_path = None
    if config.get("create_zip"):
        print()
        header("CREATING ZIP")
        zip_path = zip_dist(config["dist_dir"], config["project_name"])

    # ── Final Summary ────────────────────────────────────────────
    print_final_summary(config, failed, zip_path, start_time)


if __name__ == "__main__":
    main()
