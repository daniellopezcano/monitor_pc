#!/bin/bash

echo "Welcome to the Monitoring System Setup!"

# Step 1: Prompt user for email configuration
echo "Configuring email settings..."
read -p "Enter your sender email address: " EMAIL_SENDER
read -p "Enter your app password (e.g., from Gmail App Passwords): " EMAIL_PASSWORD
read -p "Enter the recipient email address: " EMAIL_RECEIVER

# Step 2: Prompt user for thresholds with default values
echo "Configuring alert thresholds..."
read -p "Enter the temperature threshold (°C) [default: 80]: " TEMPERATURE_THRESHOLD_C
TEMPERATURE_THRESHOLD_C=${TEMPERATURE_THRESHOLD_C:-80}

read -p "Enter the memory usage threshold (% used) [default: 90]: " MEMORY_THRESHOLD_PERCENTAGE
MEMORY_THRESHOLD_PERCENTAGE=${MEMORY_THRESHOLD_PERCENTAGE:-90}

read -p "Enter the disk space threshold (% free) [default: 10]: " DISK_THRESHOLD_PERCENTAGE
DISK_THRESHOLD_PERCENTAGE=${DISK_THRESHOLD_PERCENTAGE:-10}

# Step 3: Save configuration to a JSON file
CONFIG_FILE="monitoring/config.json"
echo "Saving configuration to $CONFIG_FILE..."
cat <<EOF > $CONFIG_FILE
{
    "EMAIL_SENDER": "$EMAIL_SENDER",
    "EMAIL_PASSWORD": "$EMAIL_PASSWORD",
    "EMAIL_RECEIVER": "$EMAIL_RECEIVER",
    "THRESHOLDS": {
        "TEMPERATURE_C": $TEMPERATURE_THRESHOLD_C,
        "MEMORY_PERCENT": $MEMORY_THRESHOLD_PERCENTAGE,
        "DISK_PERCENT": $DISK_THRESHOLD_PERCENTAGE
    }
}
EOF

# Step 4: Set up cron jobs
echo "Setting up cron jobs..."
CRON_CMD_1="* * * * * /usr/bin/python3 $(pwd)/monitoring/monitor_ram_and_sensors.py"
CRON_CMD_2="0 0 * * * /usr/bin/python3 $(pwd)/monitoring/monitor_disk.py"

(crontab -l 2>/dev/null; echo "$CRON_CMD_1") | crontab -
(crontab -l 2>/dev/null; echo "$CRON_CMD_2") | crontab -

echo "Cron jobs added successfully. Verify with 'crontab -l'."

# Step 5: Final message
echo "Installation complete! The monitoring system is now active."
echo "Alerts will be sent to the configured email address in case of issues."

