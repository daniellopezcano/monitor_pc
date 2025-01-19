#!/usr/bin/env python3

import os
import psutil  # Necesario para lecturas precisas de memoria
from email.message import EmailMessage
import smtplib
import ssl
from monitoring import get_sensors_output
from datetime import datetime, timedelta

# Step 2: Configure email settings
EMAIL_SENDER = "daniellopezcano13@gmail.com"
# Load configuration from config.json
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

with open(CONFIG_FILE, "r") as f:
    config = json.load(f)

# Email settings
EMAIL_SENDER = config["EMAIL_SENDER"]
EMAIL_PASSWORD = config["EMAIL_PASSWORD"]
EMAIL_RECEIVER = config["EMAIL_RECEIVER"]

# Step 3: Define thresholds
TEMPERATURE_THRESHOLD_C = config["THRESHOLDS"]["TEMPERATURE_C"]
MEMORY_THRESHOLD_PERCENTAGE = config["THRESHOLDS"]["MEMORY_PERCENT"]

# Step 4: Set cooldown times
MEMORY_ALERT_COOLDOWN = timedelta(hours=1)
SENSOR_ALERT_COOLDOWN = timedelta(hours=1)

# Step 5: Initialize variables for alert timestamps
last_memory_alert = None
last_sensor_alert = None

# Step 6: Define the email sending function
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

# Step 7: Extract temperatures from sensors output
def parse_sensors_output(sensors_output):
    """
    Extract temperatures from the sensors output.
    Returns a list of tuples: [(sensor_name, temperature), ...].
    """
    high_temps = []
    for line in sensors_output.splitlines():
        if "°C" in line:  # Look for lines with temperatures
            parts = line.split()
            for part in parts:
                if "°C" in part:
                    try:
                        temp = float(part.replace("°C", "").replace("+", ""))
                        high_temps.append((line, temp))
                    except ValueError:
                        continue
    return high_temps

# Step 8: Define the main function
def main():
    global last_memory_alert, last_sensor_alert
    now = datetime.now()

    # Memory Check
    if last_memory_alert is None or now - last_memory_alert > MEMORY_ALERT_COOLDOWN:
        # Use psutil to get memory usage
        mem = psutil.virtual_memory()
        total_memory_gb = mem.total / 1e+9  # Convert to GB
        used_memory_gb = mem.used / 1e+9  # Convert to GB
        used_memory_percentage = mem.percent  # Directly gives percentage used

        print(f"Total Memory: {total_memory_gb:.2f} GB")
        print(f"Used Memory: {used_memory_gb:.2f} GB ({used_memory_percentage:.2f}%)")

        # Check if usage exceeds threshold
        if used_memory_percentage > MEMORY_THRESHOLD_PERCENTAGE:
            send_email(
                "Memory Usage Alert",
                f"High memory usage detected:\n"
                f"Total Memory: {total_memory_gb:.2f} GB\n"
                f"Used Memory: {used_memory_gb:.2f} GB ({used_memory_percentage:.2f}%)\n"
                f"Threshold: {MEMORY_THRESHOLD_PERCENTAGE}%"
            )
            last_memory_alert = now

    # Sensor Check
    if last_sensor_alert is None or now - last_sensor_alert > SENSOR_ALERT_COOLDOWN:
        sensors_output = get_sensors_output()
        high_temps = parse_sensors_output(sensors_output)
        # Filter temperatures that exceed the threshold
        alert_temps = [(sensor, temp) for sensor, temp in high_temps if temp > TEMPERATURE_THRESHOLD_C]

        if alert_temps:
            alert_message = "\n".join([f"{sensor}: {temp}°C" for sensor, temp in alert_temps])
            send_email(
                "Temperature Alert",
                f"High temperature detected:\n{alert_message}"
            )
            last_sensor_alert = now

if __name__ == "__main__":
    main()
