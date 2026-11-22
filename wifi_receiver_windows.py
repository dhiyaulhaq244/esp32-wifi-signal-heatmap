"""
Wi-Fi signal mapping receiver for Windows.
Connect the laptop to the ESP32 access point before running this script.

IMPORTANT:
Windows exposes Wi-Fi signal quality as a percentage through netsh.
The dBm value written by this script is an APPROXIMATION:
    estimated_dBm = signal_percent / 2 - 100
It is not a direct RSSI measurement.
"""

import csv
import re
import subprocess
import time
from datetime import datetime
from pathlib import Path

EXPECTED_SSID = "ESP32_WIFI_TX"
SAMPLES_PER_POINT = 10
SECONDS_BETWEEN_SAMPLES = 1
OUTPUT_FILE = Path("wifi_measurements.csv")

# Measurement locations transcribed from the 25-point table in the PDF.
POINTS = [
    (0, 0), (0, 2), (0, 4),
    (2, 0), (2, 2), (2, 4),
    (4, 0), (4, 2), (4, 4),
    (0, -2), (0, -4), (2, -4), (2, -2),
    (0, -6), (2, -6), (4, -2), (4, -4), (4, -6),
    (0, -8), (2, -8), (4, -8),
    (4, -10), (2, -10), (0, -10), (0, -12),
]

def get_wifi_status():
    """Read current Wi-Fi connection details using Windows netsh."""
    result = subprocess.run(
        ["netsh", "wlan", "show", "interfaces"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False
    )
    output = result.stdout

    ssid_match = re.search(r"^\s*SSID\s*:\s*(.+?)\s*$", output, re.MULTILINE)
    signal_match = re.search(r"^\s*Signal\s*:\s*(\d+)\s*%", output, re.MULTILINE)

    if not ssid_match or not signal_match:
        raise RuntimeError(
            "Could not read SSID/signal from netsh. "
            "Check that Wi-Fi is enabled and the laptop is connected."
        )

    ssid = ssid_match.group(1).strip()
    signal_percent = int(signal_match.group(1))

    return ssid, signal_percent

def read_signal_percent():
    ssid, signal_percent = get_wifi_status()

    if ssid != EXPECTED_SSID:
        raise RuntimeError(
            f"Connected to '{ssid}', not '{EXPECTED_SSID}'. "
            "Connect to the ESP32 access point first."
        )

    return signal_percent

def estimate_dbm(signal_percent):
    # Common rough conversion; Windows percentage is not calibrated RSSI.
    return round(signal_percent / 2.0 - 100.0, 1)

def collect_point(point_number, x, y):
    readings = []

    print(f"\nPoint {point_number:02d}/25 | Coordinate: X={x} m, Y={y} m")
    input("Place the laptop at this point, keep its orientation consistent, then press ENTER...")

    for sample in range(1, SAMPLES_PER_POINT + 1):
        try:
            percent = read_signal_percent()
            readings.append(percent)
            print(
                f"  Sample {sample:02d}/{SAMPLES_PER_POINT}: "
                f"{percent}% (estimated {estimate_dbm(percent)} dBm)"
            )
        except RuntimeError as error:
            print(f"\nERROR: {error}")
            print("Reconnect to the ESP32 AP and press ENTER to retry this point.")
            input()
            return collect_point(point_number, x, y)

        time.sleep(SECONDS_BETWEEN_SAMPLES)

    average_percent = sum(readings) / len(readings)
    estimated_rssi = estimate_dbm(average_percent)

    return {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "point": point_number,
        "x_m": x,
        "y_m": y,
        "samples": len(readings),
        "average_signal_percent": round(average_percent, 1),
        "estimated_rssi_dbm": estimated_rssi,
        "measurement_method": "Windows netsh signal percentage; dBm estimated"
    }

def main():
    print("=== ESP32 Wi-Fi Signal Mapping Receiver ===")
    print(f"Expected Wi-Fi network: {EXPECTED_SSID}")
    print(f"Samples per point: {SAMPLES_PER_POINT}")
    print(f"Output CSV: {OUTPUT_FILE.resolve()}")

    try:
        ssid, signal = get_wifi_status()
        print(f"\nCurrent connection: {ssid} | Signal: {signal}%")
        if ssid != EXPECTED_SSID:
            print("Connect to the ESP32 access point before continuing.")
            return
    except (RuntimeError, FileNotFoundError) as error:
        print(f"Wi-Fi status error: {error}")
        return

    file_exists = OUTPUT_FILE.exists()
    with OUTPUT_FILE.open("a", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "timestamp", "point", "x_m", "y_m", "samples",
            "average_signal_percent", "estimated_rssi_dbm",
            "measurement_method"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        for index, (x, y) in enumerate(POINTS, start=1):
            row = collect_point(index, x, y)
            writer.writerow(row)
            csvfile.flush()
            print(
                f"Saved point {index}: mean {row['average_signal_percent']}% "
                f"(estimated {row['estimated_rssi_dbm']} dBm)"
            )

    print(f"\nMeasurement complete. Data saved to: {OUTPUT_FILE.resolve()}")
    print("Remember: estimated_rssi_dbm is approximate, not directly measured RSSI.")

if __name__ == "__main__":
    main()
