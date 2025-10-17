import requests
import json

# Đúng URL vùng châu Á (hiển thị trong thông báo lỗi của bạn)
FIREBASE_URL = "https://chaosmax-discorddata-1-default-rtdb.asia-southeast1.firebasedatabase.app/.json"

def read_data():
    res = requests.get(FIREBASE_URL)
    print("Status:", res.status_code)
    print("Response:", res.text)
    if res.status_code == 200:
        return res.json()
    else:
        return {"error": res.text}

def write_data(data):
    res = requests.put(FIREBASE_URL, json=data)
    print("Status:", res.status_code)
    print("Response:", res.text)
    return res.status_code == 200

with open("data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

write_data(data)
print(read_data())
