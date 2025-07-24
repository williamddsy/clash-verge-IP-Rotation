import requests
import time
import json
import urllib3
from datetime import datetime

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Clash API 配置
CLASH_API_BASE = "http://127.0.0.1:9097"
SECRET = ""  # 如果设置了secret，在这里填入

# 代理配置 - 通过Clash代理获取IP
PROXY_CONFIG = {
    'http': 'http://127.0.0.1:7897',
    'https': 'http://127.0.0.1:7897'
}

def get_current_ip():
    """获取当前外网IP地址（通过代理）"""
    try:
        # 使用多个IP查询服务，提高成功率
        ip_services = [
            ("httpbin", "https://httpbin.org/ip"),
            ("icanhazip", "https://icanhazip.com"),
            ("ipinfo", "https://ipinfo.io/ip"),
            ("ipify", "https://api.ipify.org?format=json")
        ]

        for name, service in ip_services:
            try:
                # 通过Clash代理请求，禁用SSL验证避免证书问题
                response = requests.get(service, proxies=PROXY_CONFIG, timeout=10, verify=False)
                if response.status_code == 200:
                    if name in ["icanhazip", "ipinfo"]:
                        return response.text.strip()
                    else:
                        data = response.json()
                        # 不同服务返回格式不同，统一处理
                        if 'ip' in data:
                            return data['ip']
                        elif 'origin' in data:
                            return data['origin']
                        elif 'query' in data:
                            return data['query']
            except Exception as e:
                print(f"  IP查询服务 {name} ({service}) 失败: {e}")
                continue
        return "Unknown"
    except Exception as e:
        print(f"  获取IP异常: {e}")
        return "Unknown"

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

def check_global_proxy():
    """检查并确保全局代理设置正确"""
    try:
        response = requests.get(f"{CLASH_API_BASE}/proxies", timeout=5)
        if response.status_code == 200:
            proxies = response.json()['proxies']
            if 'GLOBAL' in proxies:
                global_proxy = proxies['GLOBAL']
                current_selection = global_proxy.get('now', 'Unknown')
                if current_selection == 'DIRECT':
                    print("⚠️  检测到全局代理设置为DIRECT，尝试切换到IP-Rotation...")
                    switch_response = requests.put(
                        f"{CLASH_API_BASE}/proxies/GLOBAL",
                        json={"name": "IP-Rotation"},
                        timeout=5
                    )
                    if switch_response.status_code == 204:
                        print("✅ 已切换全局代理到IP-Rotation")
                        return True
                    else:
                        print(f"❌ 切换失败: {switch_response.status_code}")
                        return False
                elif current_selection == 'IP-Rotation':
                    return True
                else:
                    print(f"⚠️  全局代理当前选择: {current_selection}")
                    return True
        return False
    except Exception as e:
        print(f"检查全局代理异常: {e}")
        return False

def monitor_rotation():
    """监控节点切换和IP变化"""
    print("开始监控 IP-Rotation 组的节点切换和IP变化...")
    print(f"代理配置: {PROXY_CONFIG}")

    # 检查全局代理设置
    if not check_global_proxy():
        print("❌ 全局代理设置有问题，可能影响监控结果")

    print("=" * 80)

    last_node = None
    last_ip = None
    switch_count = 0
    start_time = datetime.now()

    while True:
        current_time = datetime.now()
        group_info = get_proxy_group_info()

        if group_info:
            current_node = group_info.get("now", "Unknown")
            print(f"[{current_time.strftime('%H:%M:%S')}] 当前节点: {current_node}")

            # 获取IP地址
            current_ip = get_current_ip()
            print(f"[{current_time.strftime('%H:%M:%S')}] 当前IP: {current_ip}")

            # 检查是否是真实IP（可能代理没有生效）
            if current_ip == "220.198.248.152":
                print(f"[{current_time.strftime('%H:%M:%S')}] ⚠️  检测到真实IP，代理可能未生效")

            if last_node is None:
                print(f"[{current_time.strftime('%H:%M:%S')}] 初始化完成")
                print("-" * 80)
            elif current_node != last_node or current_ip != last_ip:
                switch_count += 1
                elapsed = (current_time - start_time).total_seconds()

                print(f"[{current_time.strftime('%H:%M:%S')}] 变化检测 #{switch_count}:")
                if current_node != last_node:
                    print(f"  节点变化: {last_node} -> {current_node}")
                if current_ip != last_ip:
                    print(f"  IP变化: {last_ip} -> {current_ip}")

                print(f"  运行时间: {elapsed:.1f}s")
                print("-" * 80)

            last_node = current_node
            last_ip = current_ip
        else:
            print(f"[{current_time.strftime('%H:%M:%S')}] 无法获取代理组信息")

        time.sleep(5)  # 5秒检查一次

if __name__ == "__main__":
    try:
        monitor_rotation()
    except KeyboardInterrupt:
        print("\n监控已停止")
