#!/usr/bin/env python3
import os
import shutil
import numpy as np
import smtplib
from email.mime.text import MIMEText

# --- MEMORY MONITORING ---
def get_user_mem_footprint(verbose=False):
    """
    Retrieves a summary of memory usage (RAM and virtual memory) for all users with running processes.
    """
    import subprocess

    # Use `ps` to list users with active processes
    try:
        output = subprocess.check_output(
            "ps -eo user,rss,vsz --sort=user | awk '{rss[$1]+=$2; vmem[$1]+=$3} END {for (user in rss) print user, rss[user], vmem[user]}'",
            shell=True,
            text=True
        )
    except Exception as e:
        if verbose:
            print(f"Error fetching memory usage: {e}")
        return [], [], []

    names, rss, vmem = [], [], []
    for line in output.strip().split('\n'):
        try:
            user, user_rss, user_vmem = line.split()
            names.append(user)
            rss.append(float(user_rss) / 1e+6)  # Convert RSS to GB
            vmem.append(float(user_vmem) / 1e+6)  # Convert VMEM to GB
            if verbose:
                print(f"User: {user}, RSS: {float(user_rss) / 1e+6:.2f} GB, VMEM: {float(user_vmem) / 1e+6:.2f} GB")
        except ValueError:
            continue  # Skip malformed lines

    return names, rss, vmem


# --- SENSOR MONITORING ---
def get_sensors_output():
    """
    Retrieves the output of the `sensors` command.
    Returns it as a string.
    """
    return os.popen("sensors").read()

# --- DISK USAGE MONITORING ---
def get_disk_usage():
    """
    Retrieves the total, used, and free disk space.
    Returns the values in bytes.
    """
    total, used, free = shutil.disk_usage("/")
    return total, used, free

# --- TESTING FUNCTIONS ---
if __name__ == "__main__":

    # Test Memory Monitoring
    print("Testing Memory Monitoring...")
    names, rss, vmem = get_user_mem_footprint()
    print("Users:", names)
    print("RSS:", rss)
    print("VMEM:", vmem)

    # Test Sensor Monitoring
    print("\nTesting Sensor Monitoring...")
    sensors_output = get_sensors_output()
    print(sensors_output)

    # Test Disk Usage Monitoring
    print("\nTesting Disk Usage Monitoring...")
    total, used, free = get_disk_usage()
    print(f"Total: {total / 1e+9:.2f} GB, Used: {used / 1e+9:.2f} GB, Free: {free / 1e+9:.2f} GB")
