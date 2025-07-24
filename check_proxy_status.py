#!/usr/bin/env python3
import requests
import urllib3
import subprocess
import os

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def check_clash_config():
    """检查Clash配置"""
    print("=" * 60)
    print("检查 Clash 配置")
    print("=" * 60)
    
    try:
        response = requests.get("http://127.0.0.1:9097/configs", timeout=5)
        if response.status_code == 200:
            config = response.json()
            print(f"模式: {config.get('mode', 'Unknown')}")
            print(f"混合端口: {config.get('mixed-port', 'Unknown')}")
            print(f"允许局域网: {config.get('allow-lan', 'Unknown')}")
            print(f"TUN模式: {config.get('tun', {}).get('enable', 'Unknown')}")
            return True
        else:
            print(f"获取配置失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"检查配置异常: {e}")
        return False

def check_system_proxy():
    """检查系统代理设置"""
    print("\n" + "=" * 60)
    print("检查系统代理设置")
    print("=" * 60)
    
    try:
        # 检查HTTP代理环境变量
        http_proxy = os.environ.get('HTTP_PROXY') or os.environ.get('http_proxy')
        https_proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
        
        print(f"HTTP_PROXY环境变量: {http_proxy or '未设置'}")
        print(f"HTTPS_PROXY环境变量: {https_proxy or '未设置'}")
        
        # 在macOS上检查系统代理设置
        try:
            result = subprocess.run(['scutil', '--proxy'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("\nmacOS系统代理设置:")
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if 'HTTPEnable' in line or 'HTTPProxy' in line or 'HTTPPort' in line:
                        print(f"  {line}")
                    elif 'HTTPSEnable' in line or 'HTTPSProxy' in line or 'HTTPSPort' in line:
                        print(f"  {line}")
        except Exception as e:
            print(f"检查系统代理失败: {e}")
            
    except Exception as e:
        print(f"检查系统代理异常: {e}")

def test_direct_connection():
    """测试直接连接（不通过代理）"""
    print("\n" + "=" * 60)
    print("测试直接连接")
    print("=" * 60)
    
    # 测试可以工作的服务
    test_urls = [
        "http://httpbin.org/ip",  # HTTP版本
        "https://httpbin.org/ip", # HTTPS版本
    ]
    
    for url in test_urls:
        try:
            print(f"\n测试 {url}...")
            response = requests.get(url, timeout=10, verify=False)
            if response.status_code == 200:
                if url.startswith('http://'):
                    data = response.json()
                    ip = data.get('origin', 'Unknown')
                else:
                    data = response.json()
                    ip = data.get('origin', 'Unknown')
                print(f"  ✅ 成功，IP: {ip}")
            else:
                print(f"  ❌ 状态码: {response.status_code}")
        except Exception as e:
            print(f"  ❌ 失败: {e}")

def test_proxy_with_different_methods():
    """使用不同方法测试代理"""
    print("\n" + "=" * 60)
    print("测试不同代理方法")
    print("=" * 60)
    
    # 方法1: 使用requests的proxies参数
    print("\n方法1: requests proxies参数")
    try:
        proxy_config = {
            'http': 'http://127.0.0.1:7897',
            'https': 'http://127.0.0.1:7897'
        }
        response = requests.get("http://httpbin.org/ip", proxies=proxy_config, timeout=10)
        if response.status_code == 200:
            ip = response.json().get('origin', 'Unknown')
            print(f"  ✅ 成功，IP: {ip}")
        else:
            print(f"  ❌ 状态码: {response.status_code}")
    except Exception as e:
        print(f"  ❌ 失败: {e}")
    
    # 方法2: 使用SOCKS代理
    print("\n方法2: SOCKS代理")
    try:
        socks_config = {
            'http': 'socks5://127.0.0.1:7898',
            'https': 'socks5://127.0.0.1:7898'
        }
        response = requests.get("http://httpbin.org/ip", proxies=socks_config, timeout=10)
        if response.status_code == 200:
            ip = response.json().get('origin', 'Unknown')
            print(f"  ✅ 成功，IP: {ip}")
        else:
            print(f"  ❌ 状态码: {response.status_code}")
    except Exception as e:
        print(f"  ❌ 失败: {e}")

def check_ip_rotation_node():
    """检查当前IP-Rotation节点的实际IP"""
    print("\n" + "=" * 60)
    print("检查当前节点的实际IP")
    print("=" * 60)
    
    try:
        # 获取当前节点
        response = requests.get("http://127.0.0.1:9097/proxies/IP-Rotation", timeout=5)
        if response.status_code == 200:
            current_node = response.json().get('now', 'Unknown')
            print(f"当前IP-Rotation节点: {current_node}")
            
            # 尝试切换到一个不同的节点
            available_nodes = response.json().get('all', [])
            if len(available_nodes) > 1:
                # 选择一个不同的节点
                new_node = None
                for node in available_nodes:
                    if node != current_node:
                        new_node = node
                        break
                
                if new_node:
                    print(f"尝试切换到: {new_node}")
                    switch_response = requests.put(
                        "http://127.0.0.1:9097/proxies/IP-Rotation",
                        json={"name": new_node},
                        timeout=5
                    )
                    if switch_response.status_code == 204:
                        print(f"✅ 切换成功")
                        
                        # 等待一下再测试IP
                        import time
                        time.sleep(2)
                        
                        # 测试新IP
                        proxy_config = {
                            'http': 'http://127.0.0.1:7897',
                            'https': 'http://127.0.0.1:7897'
                        }
                        ip_response = requests.get("http://httpbin.org/ip", proxies=proxy_config, timeout=10)
                        if ip_response.status_code == 200:
                            new_ip = ip_response.json().get('origin', 'Unknown')
                            print(f"切换后的IP: {new_ip}")
                        
                    else:
                        print(f"❌ 切换失败: {switch_response.status_code}")
        else:
            print(f"获取节点信息失败: {response.status_code}")
    except Exception as e:
        print(f"检查节点异常: {e}")

def main():
    print("Clash 代理状态检查")
    print("=" * 60)
    
    check_clash_config()
    check_system_proxy()
    test_direct_connection()
    test_proxy_with_different_methods()
    check_ip_rotation_node()

if __name__ == "__main__":
    main()
