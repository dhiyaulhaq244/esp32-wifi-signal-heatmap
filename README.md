# ESP32 Wi-Fi Signal Mapping

- `esp32_wifi_transmitter.ino`: configures the ESP32 as a Wi-Fi SoftAP transmitter.
- `wifi_receiver_windows.py`: reads the connected Wi-Fi signal percentage on Windows, averages 10 readings at each of the 25 coordinates, and saves a CSV file.

## Important measurement limitation

Windows `netsh wlan show interfaces` reports signal quality as a percentage, not calibrated RSSI in dBm. The script records the percentage and also computes a rough estimated dBm value using `percentage / 2 - 100`. Do not present this estimate as directly measured RSSI. For scientifically comparable RSSI data, use a receiver/driver/API that exposes calibrated RSSI in dBm.

## Setup

1. Upload `esp32_wifi_transmitter.ino` to an ESP32.
2. Connect the laptop to Wi-Fi SSID `ESP32_WIFI_TX`, password `wifiheatmap`.
3. On Windows, open PowerShell in this folder.
4. Run `python wifi_receiver_windows.py`.
5. At each prompt, place the laptop at the indicated coordinate and press Enter.
6. The script writes `wifi_measurements.csv`.

Keep laptop orientation, height, and measurement conditions consistent. The 25 coordinates follow the measurement table in the supplied PDF.
