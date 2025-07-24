#!/usr/bin/env python3
import requests
import urllib3
from datetime import datetime

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_clash_api():
    """测试Clash API连接"""
    print("=" * 60)
    print("测试 Clash API 连接")
    print("=" * 60)
    
    # 测试两个可能的端口
    ports = [9090, 9097]
    working_port = None
    
    for port in ports:
        try:
            url = f"http://127.0.0.1:{port}/configs"
            print(f"\n测试端口 {port}...")
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ 端口 {port} 连接成功")
                working_port = port
                config = response.json()
                print(f"   模式: {config.get('mode', 'Unknown')}")
                print(f"   混合端口: {config.get('mixed-port', 'Unknown')}")
                break
            else:
                print(f"❌ 端口 {port} 返回状态码: {response.status_code}")
        except Exception as e:
            print(f"❌ 端口 {port} 连接失败: {e}")
    
    return working_port

def test_proxy_groups(api_port):
    """测试代理组"""
    print("\n" + "=" * 60)
    print("测试代理组")
    print("=" * 60)
    
    try:
        url = f"http://127.0.0.1:{api_port}/proxies"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            proxies = response.json()['proxies']
            
            # 检查IP-Rotation组
            if 'IP-Rotation' in proxies:
                ip_rotation = proxies['IP-Rotation']
                print(f"✅ 找到 IP-Rotation 组")
                print(f"   类型: {ip_rotation.get('type', 'Unknown')}")
                print(f"   当前节点: {ip_rotation.get('now', 'Unknown')}")
                print(f"   可用节点数: {len(ip_rotation.get('all', []))}")
                
                # 显示前5个节点
                all_nodes = ip_rotation.get('all', [])
                if all_nodes:
                    print(f"   前5个节点: {', '.join(all_nodes[:5])}")
                
                return True
            else:
                print("❌ 未找到 IP-Rotation 组")
                print("可用的代理组:")
                for name, info in proxies.items():
                    if info.get('type') in ['select', 'url-test', 'fallback']:
                        print(f"   - {name} ({info.get('type', 'Unknown')})")
                return False
        else:
            print(f"❌ 获取代理组失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 测试代理组异常: {e}")
        return False

def test_proxy_connection(api_port):
    """测试代理连接"""
    print("\n" + "=" * 60)
    print("测试代理连接")
    print("=" * 60)
    
    # 代理配置
    proxy_config = {
        'http': 'http://127.0.0.1:7897',
        'https': 'http://127.0.0.1:7897'
    }
    
    print(f"代理配置: {proxy_config}")
    
    # 测试IP查询服务
    ip_services = [
        ("ipify", "https://api.ipify.org?format=json"),
        ("httpbin", "https://httpbin.org/ip"),
        ("icanhazip", "https://icanhazip.com"),
        ("ipinfo", "https://ipinfo.io/ip")
    ]
    
    print("\n测试通过代理访问IP查询服务:")
    success_count = 0
    
    for name, url in ip_services:
        try:
            print(f"\n  测试 {name} ({url})...")
            response = requests.get(url, proxies=proxy_config, timeout=10, verify=False)
            if response.status_code == 200:
                if name in ["icanhazip", "ipinfo"]:
                    ip = response.text.strip()
                else:
                    data = response.json()
                    ip = data.get('ip') or data.get('origin') or data.get('query', 'Unknown')
                
                print(f"  ✅ 成功获取IP: {ip}")
                success_count += 1
            else:
                print(f"  ❌ 状态码: {response.status_code}")
        except Exception as e:
            print(f"  ❌ 失败: {e}")
    
    print(f"\n代理连接测试结果: {success_count}/{len(ip_services)} 成功")
    
    # 测试不通过代理的连接（获取真实IP）
    print("\n测试不通过代理的连接（真实IP）:")
    try:
        response = requests.get("https://api.ipify.org?format=json", timeout=10, verify=False)
        if response.status_code == 200:
            real_ip = response.json()['ip']
            print(f"  真实IP: {real_ip}")
        else:
            print(f"  获取真实IP失败: {response.status_code}")
    except Exception as e:
        print(f"  获取真实IP异常: {e}")
    
    return success_count > 0

def main():
    print(f"Clash 诊断工具")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 测试API连接
    working_port = test_clash_api()
    if not working_port:
        print("\n❌ 无法连接到Clash API，请检查Clash是否正在运行")
        return
    
    # 测试代理组
    has_ip_rotation = test_proxy_groups(working_port)
    
    # 测试代理连接
    proxy_works = test_proxy_connection(working_port)
    
    # 总结
    print("\n" + "=" * 60)
    print("诊断总结")
    print("=" * 60)
    print(f"✅ Clash API端口: {working_port}")
    print(f"{'✅' if has_ip_rotation else '❌'} IP-Rotation组: {'存在' if has_ip_rotation else '不存在'}")
    print(f"{'✅' if proxy_works else '❌'} 代理连接: {'正常' if proxy_works else '异常'}")
    
    if working_port and has_ip_rotation and proxy_works:
        print("\n🎉 所有测试通过！可以使用监控脚本")
        print(f"\n建议的配置:")
        print(f"CLASH_API_BASE = \"http://127.0.0.1:{working_port}\"")
    else:
        print("\n⚠️  存在问题，需要修复后再使用监控脚本")

if __name__ == "__main__":
    main()
