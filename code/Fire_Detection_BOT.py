import cv2, requests
from PIL import Image
from picamera2 import Picamera2
from ultralytics import YOLO
import os
BOT_TOKEN  = ""
CHAT_ID    = ""
SAVE_PATH  = ""
MODEL_PATH = ""
FLAG_FILE  = "sendphotos.flag"


def get_flag():
    try:
        return open(FLAG_FILE).read().strip() == "true"
    except:
        return False


def set_flag(value: bool):
    open(FLAG_FILE, "w").write("true" if value else "false")


def check_last_telegram_command():

    try:
        r = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates",
                         params={"limit": 10}, timeout=5)
        updates = r.json().get("result", [])
       
        for u in reversed(updates):
            text = u.get("message", {}).get("text", "").strip().lower()
            chat_id = str(u.get("message", {}).get("chat", {}).get("id", ""))
            if chat_id != CHAT_ID:
                continue
            if text == "sendphotos=true":
                set_flag(True)
            elif text == "sendphotos=false":
                set_flag(False)
            break  
    except Exception as e:
        print(f"[Telegram] Poll error: {e}")


def send_photo(caption):
    with open(SAVE_PATH, "rb") as photo:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
                      data={"chat_id": CHAT_ID, "caption": caption},
                      files={"photo": photo})



check_last_telegram_command()   
send_all = get_flag()         

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)}))
picam2.start()
results = YOLO(MODEL_PATH)(picam2.capture_array())
picam2.stop()

labels = {0: "Feuer", 1: "Rauch"}
alarm  = "\n".join(f"{labels[int(b.cls)]} ({float(b.conf[0])*100:.1f}%)"
                   for b in results[0].boxes if int(b.cls) in labels)

Image.fromarray(cv2.cvtColor(results[0].plot(), cv2.COLOR_BGR2RGB)).save(SAVE_PATH)

if send_all:
    caption = alarm if alarm else "Routinebild"
    send_photo(caption)
    print("Sent (send_all mode):", caption)
elif alarm:
    send_photo(alarm)
    print("Sent (detection):", alarm)
else:
    print("Nothing detected. Not sending.")

os.system("sudo shutdown now")
