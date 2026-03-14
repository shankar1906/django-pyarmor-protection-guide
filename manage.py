#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def check_license():
    license_path = os.path.join(os.path.dirname(__file__), 'license.lic')

    if not os.path.exists(license_path):
        print("=" * 60)
        print("  ❌ LICENSE ERROR")
        print("=" * 60)
        print("  No license file found.")
        print("  Please contact your software provider.")
        print("  Email: support@shan.com")
        print("  Phone: +91-XXXXXXXXXX")
        print("=" * 60)
        sys.exit(1)


def main():
    """Run administrative tasks."""
    check_license()

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flowserve_soft.settings')

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    try:
        execute_from_command_line(sys.argv)

    except RuntimeError as e:
        error = str(e)
        print("=" * 60)

        if "protection exception" in error or "license" in error.lower():
            print("  ❌ LICENSE INVALID")
            print("=" * 60)
            print("  This software is not licensed for this machine.")
            print("  Please contact your software provider.")
            print("  Email: support@shan.com")
            print("  Phone: +91-XXXXXXXXXX")

        elif "expired" in error.lower():
            print("  ❌ LICENSE EXPIRED")
            print("=" * 60)
            print("  Your software license has expired.")
            print("  Please renew your license.")
            print("  Email: support@shan.com")
            print("  Phone: +91-XXXXXXXXXX")

        else:
            print("  ❌ STARTUP ERROR")
            print("=" * 60)
            print(f"  {error}")

        print("=" * 60)
        sys.exit(1)


if __name__ == '__main__':
    main()