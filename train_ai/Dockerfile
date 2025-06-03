# Base image
FROM python:3.10-slim

# Tạo thư mục làm việc
WORKDIR /app

# Copy file vào container
COPY train.py requirements.txt ./

# Cài thư viện Python
RUN pip install --no-cache-dir -r requirements.txt

# Lệnh mặc định khi chạy container
CMD ["python", "train.py"]
