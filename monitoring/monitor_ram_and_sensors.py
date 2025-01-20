#!/usr/bin/env python3

import os
import psutil
from email.message import EmailMessage
import smtplib
import ssl
from monitoring import get_sensors_output, get_user_mem_footprint
from datetime import datetime, timedelta
import json

# Load configuration from config.json
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")
with open(CONFIG_FILE, "r") as f:
    config = json.load(f)

# Email settings
EMAIL_SENDER = config["EMAIL_SENDER"]
EMAIL_PASSWORD = config["EMAIL_PASSWORD"]
EMAIL_RECEIVER = config["EMAIL_RECEIVER"]

# Thresholds
MEMORY_THRESHOLD_PERCENTAGE = config["THRESHOLDS"]["MEMORY_PERCENT"]
TEMPERATURE_THRESHOLD_C = config["THRESHOLDS"]["TEMPERATURE_C"]

# Cooldown times
MEMORY_ALERT_COOLDOWN = timedelta(hours=1)
SENSOR_ALERT_COOLDOWN = timedelta(hours=1)

# Alert timestamps
last_memory_alert = None
last_sensor_alert = None

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

# Function to parse sensor output
def parse_sensors_output(sensors_output, verbose=False):
    high_temps = []
    for line in sensors_output.splitlines():
        if "°C" in line:
            parts = line.split()
            for part in parts:
                if "°C" in part:
                    try:
                        temp = float(part.replace("°C", "").replace("+", ""))
                        high_temps.append((line, temp))
                        if verbose:
                            print(f"Found temperature: {line}")
                    except ValueError:
                        continue
    return high_temps

# Main function
def main(verbose=False):
    global last_memory_alert, last_sensor_alert
    now = datetime.now()

    # Memory Check
    if last_memory_alert is None or now - last_memory_alert > MEMORY_ALERT_COOLDOWN:
        mem = psutil.virtual_memory()
        total_memory_gb = mem.total / 1e+9  # Convert to GB
        used_memory_gb = mem.used / 1e+9  # Convert to GB
        used_memory_percentage = mem.percent

        # Call get_user_mem_footprint to get detailed user memory usage
        names, rss, vmem = get_user_mem_footprint(verbose=verbose)

        # Calculate RSS percentage for each user
        user_rss_percentages = [
            (user, user_rss, user_vmem, (user_rss / total_memory_gb) * 100)
            for user, user_rss, user_vmem in zip(names, rss, vmem)
        ]

        # Sort users by RSS (descending)
        sorted_users = sorted(user_rss_percentages, key=lambda x: x[1], reverse=True)
        user_summary = "\n".join(
            [
                f"User: {user}, RSS: {user_rss:.2f} GB ({rss_percentage:.2f}%), VMEM: {user_vmem:.2f} GB"
                for user, user_rss, user_vmem, rss_percentage in sorted_users
            ]
        )

        if verbose:
            print(f"Total Memory: {total_memory_gb:.2f} GB")
            print(f"Used Memory: {used_memory_gb:.2f} GB ({used_memory_percentage:.2f}%)")
            print("User Memory Usage (sorted):")
            print(user_summary)

        if used_memory_percentage > MEMORY_THRESHOLD_PERCENTAGE:
            send_email(
                "Memory Usage Alert",
                f"High memory usage detected:\n"
                f"Total Memory: {total_memory_gb:.2f} GB\n"
                f"Used Memory: {used_memory_gb:.2f} GB ({used_memory_percentage:.2f}%)\n"
                f"Threshold: {MEMORY_THRESHOLD_PERCENTAGE}%\n\n"
                f"Detailed User Memory Usage (sorted):\n{user_summary}",
                verbose=verbose,
            )
            last_memory_alert = now

    # Sensor Check
    if last_sensor_alert is None or now - last_sensor_alert > SENSOR_ALERT_COOLDOWN:
        sensors_output = get_sensors_output()
        high_temps = parse_sensors_output(sensors_output, verbose=verbose)
        alert_temps = [(sensor, temp) for sensor, temp in high_temps if temp > TEMPERATURE_THRESHOLD_C]

        if alert_temps:
            alert_message = "\n".join([f"{sensor}: {temp}°C" for sensor, temp in alert_temps])
            send_email(
                "Temperature Alert",
                f"High temperature detected:\n"
                f"Threshold: {TEMPERATURE_THRESHOLD_C}°C\n"
                f"Details:\n{alert_message}",
                verbose=verbose,
            )
            last_sensor_alert = now

if __name__ == "__main__":
    # Add verbose flag for testing
    import argparse

    parser = argparse.ArgumentParser(description="Monitor RAM and Sensors.")
    parser.add_argument("--verbose", action="store_true", help="Enable detailed output for testing.")
    args = parser.parse_args()

    main(verbose=args.verbose)
