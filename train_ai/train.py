from sklearn.ensemble import IsolationForest
import pandas as pd
import joblib
import os

# Load data
df = pd.read_csv("snmp_parser/data.csv")

features = [
    "cpu", "ram", "temp",
    "GigabitEthernet1/0_in", "GigabitEthernet1/0_out",
    "GigabitEthernet2/0_in", "GigabitEthernet2/0_out",
    "GigabitEthernet3/0_in", "GigabitEthernet3/0_out"
]

# Huấn luyện mô hình Isolation Forest
model = IsolationForest(contamination=0.05, random_state=42)
model.fit(df[features])

# Lưu mô hình
joblib.dump(model, "model.joblib")
print("[+] Mô hình đã được huấn luyện và lưu tại model.joblib")
print("[DEBUG] Current dir:", os.getcwd())
print("[DEBUG] snmp_parser contents:", os.listdir("snmp_parser"))
