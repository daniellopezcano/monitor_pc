
# Monitoring System

A Python-based system for monitoring memory usage, disk space, and hardware temperatures, with automatic email notifications for alerts.

## Features
- Monitor memory, disk usage, and system temperatures.
- Receive email alerts when thresholds are exceeded.
- Automate checks with cron jobs.

---

## Testing the Monitoring System

Follow these steps to ensure that the monitoring system works as expected after downloading the repository.

---

### 1. Clone the Repository

First, clone the GitHub repository to your local machine:

```bash
git clone https://github.com/your-username/monitoring-system.git
cd monitoring-system
```

---

### 2. Review the File Structure

Ensure the repository contains the following key files:

```plaintext
monitoring-system/
├── README.md
├── LICENSE
├── install.sh
├── requirements.txt
├── monitoring/
│   ├── monitoring.py
│   ├── monitor_ram_and_sensors.py
│   ├── monitor_disk.py
│   └── config.json (generated during installation)
└── cron/
    ├── high_frequency_checks.cron
    ├── daily_disk_check.cron
```

---

### 3. Install Dependencies

Install the required Python libraries listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

---

### 4. Run the Installation Script

Run the `install.sh` script to configure the system. This will:
- Ask for email credentials.
- Set thresholds for memory, temperature, and disk usage alerts.
- Create a `config.json` file in the `monitoring/` directory.
- Set up cron jobs for automated monitoring.

```bash
bash install.sh
```

---

### 5. Validate the Configuration

After running the installation script, validate the generated `config.json` file:

```bash
cat monitoring/config.json
```

You should see something like this:

```json
{
    "EMAIL_SENDER": "your-email@example.com",
    "EMAIL_PASSWORD": "your-app-password",
    "EMAIL_RECEIVER": "recipient@example.com",
    "THRESHOLDS": {
        "TEMPERATURE_C": 80,
        "MEMORY_PERCENT": 90,
        "DISK_PERCENT": 10
    }
}
```

---

### 6. Test Individual Scripts

#### **6.1 Test `monitoring.py`**
Run the core monitoring functions and verify their output:

```bash
python monitoring/monitoring.py
```

Expected output:
- Memory usage details for active users.
- Hardware temperature details from `sensors`.
- Disk usage summary.

#### **6.2 Test `monitor_ram_and_sensors.py`**
Run the script to check RAM and sensor monitoring. If thresholds are exceeded, an email will be sent:

```bash
python monitoring/monitor_ram_and_sensors.py
```

Verify:
- No errors during execution.
- Check your inbox for an alert if any threshold is breached.

#### **6.3 Test `monitor_disk.py`**
Run the script to check disk space usage. If thresholds are exceeded, an email will be sent:

```bash
python monitoring/monitor_disk.py
```

Verify:
- No errors during execution.
- Check your inbox for a disk space alert if thresholds are breached.

---

### 7. Check Cron Jobs

Verify that the cron jobs were added correctly:

```bash
crontab -l
```

You should see entries similar to:

```plaintext
* * * * * /usr/bin/python3 /path/to/monitoring-system/monitoring/monitor_ram_and_sensors.py
0 0 * * * /usr/bin/python3 /path/to/monitoring-system/monitoring/monitor_disk.py
```

---

### 8. Simulate Alerts (Optional)

You can simulate alerts to test the email notification system:

#### **Simulate Memory Alert**
Modify the `MEMORY_THRESHOLD_PERCENTAGE` in `config.json` to a very low value (e.g., 1%) and run:

```bash
python monitoring/monitor_ram_and_sensors.py
```

#### **Simulate Disk Alert**
Modify the `DISK_THRESHOLD_PERCENTAGE` in `config.json` to a very high value (e.g., 99%) and run:

```bash
python monitoring/monitor_disk.py
```

---

### 9. Monitor Logs and Emails

During testing, ensure that:
- Emails are sent to the configured address for alerts.
- No unexpected errors occur in the terminal.

---

### 10. Troubleshooting

If you encounter any issues:
1. Check the Python version:
   ```bash
   python --version
   ```
   Ensure it’s 3.6 or later.

2. Verify email credentials in `config.json`.
3. Check system logs for errors in cron:
   ```bash
   cat /var/log/syslog | grep CRON
   ```

---

With these steps, you should have a fully functional monitoring system ready to automate resource and hardware monitoring. Let us know if you need further clarification! 😊
