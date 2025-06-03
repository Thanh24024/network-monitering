# Sử dụng Python image nhẹ
FROM python:3.10-slim

# Tạo thư mục ứng dụng
WORKDIR /app

# Sao chép mã và log vào container
COPY parse_snmp_log.py ./

# Cài thư viện cần thiết
RUN pip install pandas

# Lệnh chạy mặc định
CMD ["python", "parse_snmp_log.py"]
