import logging

class TruncateFormatter(logging.Formatter):
    def format(self, record):
        msg = super().format(record)
        if len(msg) > 1200:
            return msg[:1197] + "..."
        return msg

def setup_logging():
    # Xóa các handler mặc định
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Formatter chung
    formatter = TruncateFormatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Handler console (INFO trở lên)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Handler file log chung (INFO trở lên)
    file_handler = logging.FileHandler("bot.log", encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # Handler file debug riêng (chỉ DEBUG)
    debug_handler = logging.FileHandler("debug.log", encoding="utf-8")
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(formatter)

    # Cấu hình logging (không dùng basicConfig nữa)
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # để capture được DEBUG
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(debug_handler)
