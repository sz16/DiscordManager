# Dùng image Python 3.10 chính thức
FROM python:3.10-slim

# Đặt thư mục làm việc
WORKDIR /app

# Copy toàn bộ mã nguồn vào container
COPY . .

# Cài đặt các thư viện cần thiết
RUN pip install --no-cache-dir -r requirements.txt

# Lệnh mặc định khi container khởi động
CMD ["python", "main.py"]
