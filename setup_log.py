import logging

class TruncateFormatter(logging.Formatter):
    def format(self, record):
        # Lấy message đã format theo kiểu chuẩn
        msg = super().format(record)
        # Nếu dài quá 120 ký tự thì cắt + thêm "..."
        if len(msg) > 600:
            return msg[:597] + "..."
        return msg

def setup_logging():
    # Xóa handler mặc định (discord.py hay thêm 1 cái)
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Tạo formatter giới hạn 120 ký tự
    formatter = TruncateFormatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Tạo handler console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Tạo handler file (nếu muốn ghi đầy đủ vào file log)
    file_handler = logging.FileHandler("bot.log", encoding="utf-8")
    file_handler.setFormatter(formatter)

    # Cấu hình logging
    logging.basicConfig(
        level=logging.INFO,
        handlers=[console_handler, file_handler]
    )
