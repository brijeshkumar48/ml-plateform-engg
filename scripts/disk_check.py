import os
import shutil

path = os.getenv("CHECK_PATH", ".")
total, used, free = shutil.disk_usage(path)
percent = used / total * 100

print(f"Path: {os.path.abspath(path)}")
print(f"Disk usage: {percent:.1f}%")
print("ALERT: disk usage >= 80%" if percent >= 80 else "STATUS: OK")
