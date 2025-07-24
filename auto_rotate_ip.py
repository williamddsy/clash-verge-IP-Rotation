import requests
import time
from datetime import datetime

def auto_rotate_ip():
    """自动轮换IP-Rotation组的节点"""
    proxies = [
        # B1 系列 (更多节点)
        "GLaDOS-B1-01", "GLaDOS-B1-02", "GLaDOS-B1-03", "GLaDOS-B1-04",
        "GLaDOS-B1-05", "GLaDOS-B1-06", "GLaDOS-B1-07", "GLaDOS-B1-08",
        
        # T3 系列 (新增)
        "GLaDOS-T3-01", "GLaDOS-T3-02", "GLaDOS-T3-03", "GLaDOS-T3-04",
        "GLaDOS-T3-05", "GLaDOS-T3-06",
        
        # US 系列 (更多节点)
        "GLaDOS-US-01", "GLaDOS-US-02", "GLaDOS-US-03", "GLaDOS-US-04",
        "GLaDOS-US-05", "GLaDOS-US-06",
        
        # TW 系列 (更多节点)
        "GLaDOS-TW-01", "GLaDOS-TW-02", "GLaDOS-TW-03", "GLaDOS-TW-04",
        "GLaDOS-TW-05", "GLaDOS-TW-06",
        
        # JP 系列 (更多节点)
        "GLaDOS-JP-01", "GLaDOS-JP-02", "GLaDOS-JP-03",
        
        # SG 系列 (更多节点)
        "GLaDOS-SG-01", "GLaDOS-SG-02", "GLaDOS-SG-03",
        
        # HK 系列 (更多节点)
        "GLaDOS-HK-01", "GLaDOS-HK-02", "GLaDOS-HK-03",
        
        # D1 系列 (新增)
        "GLaDOS-D1-01", "GLaDOS-D1-02", "GLaDOS-D1-03"
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
