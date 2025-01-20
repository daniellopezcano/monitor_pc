#!/usr/bin/env python3

import os
import json
import shutil
from email.message import EmailMessage
import smtplib
import ssl

# Load configuration from config.json
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")
with open(CONFIG_FILE, "r") as f:
    config = json.load(f)

# Email settings
EMAIL_SENDER = config["EMAIL_SENDER"]
EMAIL_PASSWORD = config["EMAIL_PASSWORD"]
EMAIL_RECEIVER = config["EMAIL_RECEIVER"]

# Disk settings
DISK_MONITOR_DIR = config["DISK_MONITOR_DIR"]
DISK_THRESHOLD_PERCENTAGE = config["THRESHOLDS"]["DISK_PERCENT"]
DISK_MAX_SIZE_GB = config["DISK_MAX_SIZE_GB"]

# Email sending function
def send_email(subject, body, verbose=False):
    if verbose:
        print(f"Sending email with subject: {subject}")
    em = EmailMessage()
    em["From"] = EMAIL_SENDER
    em["To"] = EMAIL_RECEIVER
    em["Subject"] = subject
    em.set_content(body)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
        smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
        smtp.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, em.as_string())
    if verbose:
        print("Email sent successfully!")

# Calculate the size of a directory (first-level subdirectories only)
def calculate_directory_size_first_level(directory, verbose=False):
    total_size = 0
    subdirs_sizes = []

    if verbose:
        print(f"Analyzing subdirectories in: {directory}")

    # Iterate over first-level subdirectories
    try:
        for entry in os.scandir(directory):
            if entry.is_dir(follow_symlinks=False):
                subdir_size = 0
                for root, _, files in os.walk(entry.path):
                    for f in files:
                        fp = os.path.join(root, f)
                        try:
                            subdir_size += os.path.getsize(fp)
                        except FileNotFoundError:
                            if verbose:
                                print(f"File not found: {fp}")
                        except PermissionError:
                            if verbose:
                                print(f"Permission denied: {fp}")
                        except Exception as e:
                            if verbose:
                                print(f"Error accessing {fp}: {e}")
                subdirs_sizes.append((entry.path, subdir_size))
                total_size += subdir_size
                if verbose:
                    print(f"Subdirectory: {entry.path}, Size: {subdir_size / 1e+9:.6f} GB")
    except PermissionError as e:
        if verbose:
            print(f"Permission denied for directory: {directory}, Error: {e}")

    return total_size, subdirs_sizes

# Main function
def main(verbose=False):
    if verbose:
        print(f"Monitoring directory: {DISK_MONITOR_DIR}")

    # Calculate the size of the monitored directory (first-level subdirectories only)
    dir_size_bytes, subdirs_sizes = calculate_directory_size_first_level(DISK_MONITOR_DIR, verbose=verbose)
    dir_size_gb = dir_size_bytes / 1e+9

    # Calculate percentage of the maximum allowed size
    used_percentage = (dir_size_gb / DISK_MAX_SIZE_GB) * 100

    if verbose:
        print(f"Directory: {DISK_MONITOR_DIR}")
        print(f"Directory Size: {dir_size_gb:.6f} GB")
        print(f"Max Allowed Size: {DISK_MAX_SIZE_GB:.2f} GB")
        print(f"Used Percentage: {used_percentage:.2f}%")

    # Prepare summary of subdirectories
    subdirs_summary = "\n".join(
        [f"{path}: {size / 1e+9:.6f} GB" for path, size in sorted(subdirs_sizes, key=lambda x: x[1], reverse=True)]
    )

    # Check if usage exceeds thresholds
    if used_percentage > DISK_THRESHOLD_PERCENTAGE:
        if verbose:
            print("Disk usage threshold exceeded.")
        send_email(
            "Disk Space Alert",
            f"Low disk space detected in directory {DISK_MONITOR_DIR}:\n\n"
            f"Directory Size: {dir_size_gb:.2f} GB\n"
            f"Max Allowed Size: {DISK_MAX_SIZE_GB:.2f} GB\n"
            f"Used Percentage: {used_percentage:.2f}%\n\n"
            f"Top-level Subdirectories:\n{subdirs_summary}",
            verbose=verbose
        )
    else:
        if verbose:
            print("Disk usage is within normal limits.")

if __name__ == "__main__":
    # Add verbose flag for testing
    import argparse

    parser = argparse.ArgumentParser(description="Monitor Disk Usage.")
    parser.add_argument("--verbose", action="store_true", help="Enable detailed output for testing.")
    args = parser.parse_args()

    main(verbose=args.verbose)
