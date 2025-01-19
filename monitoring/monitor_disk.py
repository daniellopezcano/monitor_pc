#!/usr/bin/env python3

# Step 1: Import necessary libraries
import os
import json
import shutil  # Make sure to import shutil
from email.message import EmailMessage
import smtplib
import ssl
from monitoring import get_disk_usage  # Using the function defined in monitoring.py

# Step 2: Configure email settings
# Load configuration from config.json
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

with open(CONFIG_FILE, "r") as f:
    config = json.load(f)

# Email settings
EMAIL_SENDER = config["EMAIL_SENDER"]
EMAIL_PASSWORD = config["EMAIL_PASSWORD"]
EMAIL_RECEIVER = config["EMAIL_RECEIVER"]

# Step 3: Define the disk usage threshold
DISK_THRESHOLD_PERCENTAGE = config["THRESHOLDS"]["DISK_PERCENT"]

# Step 4: Define the email sending function
def send_email(subject, body):
    em = EmailMessage()
    em["From"] = EMAIL_SENDER
    em["To"] = EMAIL_RECEIVER
    em["Subject"] = subject
    em.set_content(body)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
        smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
        smtp.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, em.as_string())
        print(f"Email sent: {subject}")

# Step 5: Analyze first-level subdirectory sizes
def analyze_subdirectories_first_level(path="/home", max_entries=5):
    """
    Analyze the sizes of subdirectories at the first level of the given path.
    Returns the top N directories consuming space.
    """
    subdirs = []
    try:
        # List first-level subdirectories
        for entry in os.scandir(path):
            if entry.is_dir(follow_symlinks=False):
                try:
                    # Calculate the size of the directory (non-recursively)
                    dir_size = sum(
                        os.path.getsize(os.path.join(entry.path, file))
                        for file in os.listdir(entry.path)
                        if os.path.isfile(os.path.join(entry.path, file))
                    )
                    subdirs.append((entry.path, dir_size))
                except Exception as e:
                    print(f"Error calculating size for {entry.path}: {e}")
    except Exception as e:
        print(f"Error accessing directory {path}: {e}")

    # Sort subdirectories by size in descending order
    subdirs.sort(key=lambda x: x[1], reverse=True)

    # Format the results
    subdir_summary = "\n".join(
        [f"{path}: {size / 1e+9:.2f} GB" for path, size in subdirs[:max_entries]]
    )
    return subdir_summary

# Step 6: Adjust `get_disk_usage` for /home
def get_home_disk_usage():
    """
    Retrieves the total, used, and free disk space for the /home partition.
    """
    total, used, free = shutil.disk_usage("/home")
    return total, used, free

# Step 7: Define the main function
def main():
    # Get disk usage for /home
    total, used, free = get_home_disk_usage()
    used_percentage = (used / total) * 100
    free_percentage = 100 - used_percentage

    # Format disk usage summary
    disk_summary = (
        f"Total disk space: {total / 1e+9:.2f} GB\n"
        f"Used disk space: {used / 1e+9:.2f} GB ({used_percentage:.2f}%)\n"
        f"Free disk space: {free / 1e+9:.2f} GB ({free_percentage:.2f}%)\n"
    )

    # Check if free space is below the threshold
    if free_percentage < DISK_THRESHOLD_PERCENTAGE:
        print("Disk usage threshold exceeded.")
        # Analyze subdirectories at the first level
        subdir_summary = analyze_subdirectories_first_level("/home", max_entries=5)
        # Send email alert with detailed analysis
        send_email(
            "Disk Space Alert",
            f"Low disk space detected on /home:\n\n{disk_summary}\n\n"
            f"Top directories consuming space:\n{subdir_summary}"
        )
    else:
        print("Disk usage is within normal limits.")

if __name__ == "__main__":
    main()
