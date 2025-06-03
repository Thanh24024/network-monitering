import re
import pandas as pd

log_file = "snmp_log"
output_csv = "data.csv"

rows = []

with open(log_file, "r") as f:
    for line in f:
        try:
            # Lấy timestamp
            timestamp_match = re.match(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+)", line)
            timestamp = timestamp_match.group(1) if timestamp_match else None

            # CPU
            cpu_match = re.search(r"CPU=(\d+)%", line)
            cpu = int(cpu_match.group(1)) if cpu_match else None

            # RAM
            ram_match = re.search(r"Mem=(\d+)%", line)
            ram = int(ram_match.group(1)) if ram_match else None

            # Temp: lấy nhiệt độ trung bình
            temp_match = re.search(r"Temp=\[([0-9,]+)\]", line)
            if temp_match:
                temps = list(map(int, temp_match.group(1).split(',')))
                temp_avg = sum(temps) / len(temps)
            else:
                temp_avg = None

            # Interfaces
            interfaces = {}
            if_match = re.search(r'IF="(.*?)"$', line)
            if if_match:
                if_string = if_match.group(1)
                pattern = re.findall(r'\["([^"]+)"\] IN:(\d+)KB OUT:(\d+)KB', if_string)
                for iface, in_kb, out_kb in pattern:
                    interfaces[iface + "_in"] = int(in_kb)
                    interfaces[iface + "_out"] = int(out_kb)

            # Gộp dữ liệu
            row = {
                "timestamp": timestamp,
                "cpu": cpu,
                "ram": ram,
                "temp": temp_avg,
            }

            # Thêm từng cổng IF nếu có
            for k in ["GigabitEthernet1/0", "GigabitEthernet2/0", "GigabitEthernet3/0"]:
                row[k + "_in"] = interfaces.get(k + "_in", 0)
                row[k + "_out"] = interfaces.get(k + "_out", 0)

            rows.append(row)

        except Exception as e:
            print(f"[!] Lỗi khi xử lý dòng: {line.strip()} -> {e}")

# Xuất ra CSV
df = pd.DataFrame(rows)
df.to_csv(output_csv, index=False)
print(f"[+] Đã trích xuất {len(df)} dòng dữ liệu vào {output_csv}")
