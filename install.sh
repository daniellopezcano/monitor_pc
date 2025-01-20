#!/bin/bash

CONFIG_FILE="./monitoring/config.json"

echo "Configuring the monitoring system..."

# Prompt for email credentials
read -p "Enter the sender email: " EMAIL_SENDER
read -p "Enter the sender email password: " EMAIL_PASSWORD
read -p "Enter the receiver email: " EMAIL_RECEIVER

# Prompt for thresholds
read -p "Enter the temperature threshold (default: 80): " TEMPERATURE_THRESHOLD_C
TEMPERATURE_THRESHOLD_C=${TEMPERATURE_THRESHOLD_C:-80}

read -p "Enter the memory usage threshold (%) (default: 90): " MEMORY_THRESHOLD_PERCENTAGE
MEMORY_THRESHOLD_PERCENTAGE=${MEMORY_THRESHOLD_PERCENTAGE:-90}

read -p "Enter the disk usage threshold (%) (default: 10): " DISK_THRESHOLD_PERCENTAGE
DISK_THRESHOLD_PERCENTAGE=${DISK_THRESHOLD_PERCENTAGE:-10}

# Prompt for disk monitoring settings
read -p "Enter the directory to monitor for disk usage (default: /home): " DISK_MONITOR_DIR
DISK_MONITOR_DIR=${DISK_MONITOR_DIR:-/home}

# Get the total disk size for the specified directory
DISK_TOTAL_SIZE=$(df -BG "$DISK_MONITOR_DIR" | awk 'NR==2 {print $2}' | sed 's/G//')

# Prompt for maximum allowed size, with the default set to the total disk size
read -p "Enter the maximum allowed size for the monitored directory (GB) (default: $DISK_TOTAL_SIZE): " DISK_MAX_SIZE_GB
DISK_MAX_SIZE_GB=${DISK_MAX_SIZE_GB:-$DISK_TOTAL_SIZE}

# Write configuration to config.json
cat <<EOF > "$CONFIG_FILE"
{
    "EMAIL_SENDER": "$EMAIL_SENDER",
    "EMAIL_PASSWORD": "$EMAIL_PASSWORD",
    "EMAIL_RECEIVER": "$EMAIL_RECEIVER",
    "THRESHOLDS": {
        "TEMPERATURE_C": $TEMPERATURE_THRESHOLD_C,
        "MEMORY_PERCENT": $MEMORY_THRESHOLD_PERCENTAGE,
        "DISK_PERCENT": $DISK_THRESHOLD_PERCENTAGE
    },
    "DISK_MONITOR_DIR": "$DISK_MONITOR_DIR",
    "DISK_MAX_SIZE_GB": $DISK_MAX_SIZE_GB
}
EOF

echo "Configuration saved to $CONFIG_FILE."

# Set up cron jobs
echo "Setting up cron jobs..."
CRON_CMD_1="* * * * * /usr/bin/python3 $(pwd)/monitoring/monitor_ram_and_sensors.py"
CRON_CMD_2="0 0 * * * /usr/bin/python3 $(pwd)/monitoring/monitor_disk.py"

(crontab -l 2>/dev/null; echo "$CRON_CMD_1") | crontab -
(crontab -l 2>/dev/null; echo "$CRON_CMD_2") | crontab -

echo "Cron jobs added successfully. Verify with 'crontab -l'."
