#!/usr/bin/env python3
import os
import shutil
import numpy as np
import smtplib
from email.mime.text import MIMEText

# --- MEMORY MONITORING ---
def get_user_mem_footprint():
    """
    Retrieves a summary of memory usage (RAM and virtual memory) for each user on the system.
    Returns the summary as a string.
    """
    import pwd
    # List all system users
    all_users = [x[0] for x in pwd.getpwall()]

    # Identify active users with running processes
    active_users = []
    for user in os.listdir('/home/'):
        if user in all_users:
            active_users.append(user)

    # Create a temporary file with the list of active users
    with open('.tmp-users', 'w') as f:
        for user in active_users:
            f.write(user + '\n')

    # Command to retrieve memory usage per user
    comm = """#!/bin/bash
    (echo "user rss(Gb) vmem(Gb)";
    for user in $(cat .tmp-users); do
        echo $user $(ps -U $user --no-headers -o rss,vsz \
        | awk '{rss+=$1/1048576; vmem+=$2/1048576} END{print rss" "vmem}')
    done | sort -k3
    ) | column -t > .tmp-mem-use
    """
    os.system(comm)

    # Process the temporary file to create a detailed message
    names, rss, vmem = [], [], []
    with open('.tmp-mem-use', 'r') as f:
        for i, line in enumerate(f.readlines()):
            if i == 0:  # Skip header
                continue
            columns = line.split()
            if len(columns) >= 3:
                names.append(columns[0])
                rss.append(float(columns[1]))
                vmem.append(float(columns[2]))

    # Clean up temporary files
    os.remove('.tmp-users')
    os.remove('.tmp-mem-use')

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
