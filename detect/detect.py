import pandas as pd
import joblib
import time
import os
import requests

# URL webhook Discord
DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/1329267219514916989/qCOWZooQUZUxQ5ccZX2mbD_UeO8avhZGSWsuM6iRcQ07xmrFRWFRcUr-q3skGFcSP0PX'

# Hàm gửi thông báo lên Discord
def send_discord_alert(msg):
    payload = {"content": msg}
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        if response.status_code != 204:
            print(f"[!] Lỗi gửi Discord: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"[!] Lỗi kết nối Discord: {e}")

print("[+] Bắt đầu giám sát bất thường...")

# Load model 1 lần
model = joblib.load("train_ai/model.joblib")

# Danh sách các đặc trưng
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

        new_data[new_data["anomaly"] == "Bất thường"].to_csv(
            "outputs/anomalies.csv", mode='a', index=False,
            header=not os.path.exists("outputs/anomalies.csv")
        )

        new_data.to_csv(
            "outputs/outputs.csv", mode='a', index=False,
            header=not os.path.exists("outputs/outputs.csv")
        )

        print(new_data[["timestamp", "cpu", "ram", "temp", "anomaly"]])

        # Gửi cảnh báo nếu phát hiện bất thường
        anomalies = new_data[new_data["anomaly"] == "Bất thường"]
        for _, row in anomalies.iterrows():
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

    time.sleep(30)
