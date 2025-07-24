import requests
import time
import json
from datetime import datetime

# Clash API 配置
CLASH_API_BASE = "http://127.0.0.1:9097"
SECRET = ""  # 如果设置了secret，在这里填入

def get_proxy_group_info(group_name="IP-Rotation"):
    """获取代理组信息"""
    try:
        headers = {}
        if SECRET:
            headers["Authorization"] = f"Bearer {SECRET}"
        
        response = requests.get(f"{CLASH_API_BASE}/proxies/{group_name}", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"API请求失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"请求异常: {e}")
        return None

def monitor_rotation():
    """监控节点切换"""
    print("开始监控 IP-Rotation 组的节点切换...")
    print("=" * 60)
    
    last_node = None
    switch_count = 0
    start_time = datetime.now()
    
    while True:
        current_time = datetime.now()
        group_info = get_proxy_group_info()
        
        if group_info:
            current_node = group_info.get("now", "Unknown")
            
            if last_node is None:
                print(f"[{current_time.strftime('%H:%M:%S')}] 初始节点: {current_node}")
            elif current_node != last_node:
                switch_count += 1
                elapsed = (current_time - start_time).total_seconds()
                print(f"[{current_time.strftime('%H:%M:%S')}] 节点切换 #{switch_count}: {last_node} -> {current_node} (运行{elapsed:.1f}s)")
            
            last_node = current_node
        else:
            print(f"[{current_time.strftime('%H:%M:%S')}] 无法获取代理组信息")
        
        time.sleep(1)  # 每秒检查一次

if __name__ == "__main__":
    try:
        monitor_rotation()
    except KeyboardInterrupt:
        print("\n监控已停止")