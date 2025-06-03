import pandas as pd
import joblib
import time
import os
import requests
import sys

# URL webhook Discord
DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/1379434925593460766/KrHC1lcCKEBqjmxO6JxQkFqq2frVanMR_j33mpBxki0ARWCwQPGeZwl12PM0ryj7xswi'

# Hàm gửi cảnh báo lên Discord
def send_discord_alert(msg):
    payload = {"content": msg}
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        if response.status_code != 204:
            print(f"[!] Lỗi gửi Discord: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"[!] Lỗi kết nối Discord: {e}")

# Hàm in log bất thường ra stdout (cho Promtail)
def log_anomaly(row):
    log_line = f"{row['timestamp']},{row['cpu']},{row['ram']},{row['temp']}," \
               f"{row['GigabitEthernet1/0_in']},{row['GigabitEthernet1/0_out']}," \
               f"{row['GigabitEthernet2/0_in']},{row['GigabitEthernet2/0_out']}," \
               f"{row['GigabitEthernet3/0_in']},{row['GigabitEthernet3/0_out']}," \
               f"{row['anomaly']}"
    print(log_line)
    sys.stdout.flush()

print("[+] Bắt đầu giám sát bất thường...")

# Load model 1 lần
model = joblib.load("train_ai/model.joblib")

features = [
    "cpu", "ram", "temp",
    "GigabitEthernet1/0_in", "GigabitEthernet1/0_out",
    "GigabitEthernet2/0_in", "GigabitEthernet2/0_out",
    "GigabitEthernet3/0_in", "GigabitEthernet3/0_out"
]

last_row = 0

while True:
    try:
        df = pd.read_csv("snmp_parser/data.csv")

        if last_row >= len(df):
            time.sleep(30)
            continue

        new_data = df.iloc[last_row:].copy()
        last_row = len(df)

        missing = [f for f in features if f not in new_data.columns]
        if missing:
            raise ValueError(f"Các cột sau không có trong dữ liệu: {missing}")

        pred = model.predict(new_data[features])
        new_data["anomaly"] = ["Bình thường" if p == 1 else "Bất thường" for p in pred]

        if not os.path.exists("outputs"):
            os.makedirs("outputs")

        new_data.to_csv(
            "outputs/outputs.csv", mode='a', index=False,
            header=not os.path.exists("outputs/outputs.csv")
        )

        anomalies = new_data[new_data["anomaly"] == "Bất thường"]
        anomalies.to_csv(
            "outputs/anomalies.csv", mode='a', index=False,
            header=not os.path.exists("outputs/anomalies.csv")
        )

        # In log bất thường ra stdout để Promtail đẩy vào Loki
        for _, row in anomalies.iterrows():
            log_anomaly(row)

            # Gửi cảnh báo lên Discord
            msg = f"""🚨 **Phát hiện bất thường**
🕒 Thời gian: `{row['timestamp']}`
💻 CPU: `{row['cpu']}%`, RAM: `{row['ram']}%`, Nhiệt độ: `{row['temp']}`
📊 G1: `{row['GigabitEthernet1/0_in']}↓ / {row['GigabitEthernet1/0_out']}↑`
📊 G2: `{row['GigabitEthernet2/0_in']}↓ / {row['GigabitEthernet2/0_out']}↑`
📊 G3: `{row['GigabitEthernet3/0_in']}↓ / {row['GigabitEthernet3/0_out']}↑`
"""
            send_discord_alert(msg)

    except Exception as e:
        print(f"[!] Lỗi: {e}")
        sys.stdout.flush()

    time.sleep(30)
