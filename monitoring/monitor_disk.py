#!/usr/bin/env python3

import os
import json
import shutil  # For disk usage
from email.message import EmailMessage
import smtplib
import ssl
from monitoring import get_disk_usage  # Using the function defined in monitoring.py

# Load configuration from config.json
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

with open(CONFIG_FILE, "r") as f:
    config = json.load(f)

# Email settings
EMAIL_SENDER = config["EMAIL_SENDER"]
EMAIL_PASSWORD = config["EMAIL_PASSWORD"]
EMAIL_RECEIVER = config["EMAIL_RECEIVER"]

# Disk usage threshold
DISK_THRESHOLD_PERCENTAGE = config["THRESHOLDS"]["DISK_PERCENT"]

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

# Analyze first-level subdirectory sizes
def analyze_subdirectories_first_level(path="/home", max_entries=5, verbose=False):
    """
    Analyze the sizes of subdirectories at the first level of the given path.
    Returns the top N directories consuming space.
    """
    subdirs = []
    try:
        for entry in os.scandir(path):
            if entry.is_dir(follow_symlinks=False):
                try:
                    dir_size = sum(
                        os.path.getsize(os.path.join(entry.path, file))
                        for file in os.listdir(entry.path)
                        if os.path.isfile(os.path.join(entry.path, file))
                    )
                    subdirs.append((entry.path, dir_size))
                    if verbose:
                        print(f"Directory: {entry.path}, Size: {dir_size / 1e+9:.2f} GB")
                except Exception as e:
                    if verbose:
                        print(f"Error calculating size for {entry.path}: {e}")
    except Exception as e:
        if verbose:
            print(f"Error accessing directory {path}: {e}")

    subdirs.sort(key=lambda x: x[1], reverse=True)
    subdir_summary = "\n".join(
        [f"{path}: {size / 1e+9:.2f} GB" for path, size in subdirs[:max_entries]]
    )
    return subdir_summary

# Get disk usage for /home
def get_home_disk_usage(verbose=False):
    """
    Retrieves the total, used, and free disk space for the /home partition.
    """
    total, used, free = shutil.disk_usage("/home")
    if verbose:
        print(f"Disk Usage - Total: {total / 1e+9:.2f} GB, Used: {used / 1e+9:.2f} GB, Free: {free / 1e+9:.2f} GB")
    return total, used, free

# Main function
def main(verbose=False):
    total, used, free = get_home_disk_usage(verbose=verbose)
    used_percentage = (used / total) * 100
    free_percentage = 100 - used_percentage

    disk_summary = (
        f"Total disk space: {total / 1e+9:.2f} GB\n"
        f"Used disk space: {used / 1e+9:.2f} GB ({used_percentage:.2f}%)\n"
        f"Free disk space: {free / 1e+9:.2f} GB ({free_percentage:.2f}%)\n"
    )

    if verbose:
        print("Disk Usage Summary:")
        print(disk_summary)

    if free_percentage < DISK_THRESHOLD_PERCENTAGE:
        if verbose:
            print("Disk usage threshold exceeded.")
        subdir_summary = analyze_subdirectories_first_level("/home", max_entries=5, verbose=verbose)
        send_email(
            "Disk Space Alert",
            f"Low disk space detected on /home:\n\n{disk_summary}\n\n"
            f"Top directories consuming space:\n{subdir_summary}",
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

