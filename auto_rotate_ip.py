import requests
import time
from datetime import datetime

def auto_rotate_ip():
    """自动轮换IP-Rotation组的节点"""
    proxies = [
        "GLaDOS-B1-01", "GLaDOS-B1-02", "GLaDOS-B1-03", "GLaDOS-B1-04",
        "GLaDOS-US-01", "GLaDOS-US-02", "GLaDOS-TW-01", "GLaDOS-TW-02",
        "GLaDOS-HK-01", "GLaDOS-HK-02", "GLaDOS-JP-01", "GLaDOS-SG-01"
    ]
    
    index = 0
    while True:
        proxy = proxies[index % len(proxies)]
        try:
            response = requests.put(
                "http://127.0.0.1:9097/proxies/IP-Rotation",
                json={"name": proxy}
            )
            if response.status_code == 204:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 切换到: {proxy}")
            else:
                print(f"切换失败: {response.status_code}")
        except Exception as e:
            print(f"请求异常: {e}")
        
        index += 1
        time.sleep(5)

if __name__ == "__main__":
    auto_rotate_ip()