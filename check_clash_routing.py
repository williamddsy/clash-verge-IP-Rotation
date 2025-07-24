#!/usr/bin/env python3
import requests
import urllib3

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def check_proxy_selection():
    """检查代理选择"""
    print("=" * 60)
    print("检查代理选择")
    print("=" * 60)
    
    try:
        response = requests.get("http://127.0.0.1:9097/proxies", timeout=5)
        if response.status_code == 200:
            proxies = response.json()['proxies']
            
            # 检查主要的代理组
            important_groups = ['GLOBAL', 'Proxy', 'Auto', 'Auto-Fast', 'IP-Rotation']
            
            for group_name in important_groups:
                if group_name in proxies:
                    group = proxies[group_name]
                    print(f"\n{group_name}:")
                    print(f"  类型: {group.get('type', 'Unknown')}")
                    print(f"  当前选择: {group.get('now', 'Unknown')}")
                    if 'all' in group and len(group['all']) > 0:
                        print(f"  可选项: {', '.join(group['all'][:5])}{'...' if len(group['all']) > 5 else ''}")
            
            # 特别检查GLOBAL或主代理的选择
            if 'GLOBAL' in proxies:
                global_proxy = proxies['GLOBAL']
                current_global = global_proxy.get('now', 'Unknown')
                print(f"\n🔍 全局代理当前选择: {current_global}")
                
                # 如果全局代理选择的是DIRECT，这就是问题所在
                if current_global == 'DIRECT':
                    print("❌ 问题发现：全局代理选择了DIRECT，所有流量都直连！")
                    return False
                elif current_global == 'IP-Rotation':
                    print("✅ 全局代理正确选择了IP-Rotation")
                    return True
                else:
                    print(f"⚠️  全局代理选择了: {current_global}")
                    return False
            else:
                print("⚠️  未找到GLOBAL代理组")
                return False
                
        else:
            print(f"获取代理信息失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"检查代理选择异常: {e}")
        return False

def fix_global_proxy():
    """修复全局代理设置"""
    print("\n" + "=" * 60)
    print("修复全局代理设置")
    print("=" * 60)
    
    try:
        # 首先检查是否有GLOBAL组
        response = requests.get("http://127.0.0.1:9097/proxies", timeout=5)
        if response.status_code == 200:
            proxies = response.json()['proxies']
            
            # 寻找主要的代理组
            main_proxy_group = None
            if 'GLOBAL' in proxies:
                main_proxy_group = 'GLOBAL'
            elif 'Proxy' in proxies:
                main_proxy_group = 'Proxy'
            elif 'Auto' in proxies:
                main_proxy_group = 'Auto'
            
            if main_proxy_group:
                print(f"找到主代理组: {main_proxy_group}")
                
                # 检查当前选择
                current_selection = proxies[main_proxy_group].get('now', 'Unknown')
                print(f"当前选择: {current_selection}")
                
                # 如果当前选择是DIRECT，切换到IP-Rotation
                if current_selection == 'DIRECT':
                    print("尝试切换到IP-Rotation...")
                    switch_response = requests.put(
                        f"http://127.0.0.1:9097/proxies/{main_proxy_group}",
                        json={"name": "IP-Rotation"},
                        timeout=5
                    )
                    if switch_response.status_code == 204:
                        print("✅ 成功切换到IP-Rotation")
                        return True
                    else:
                        print(f"❌ 切换失败: {switch_response.status_code}")
                        return False
                elif current_selection == 'IP-Rotation':
                    print("✅ 已经选择了IP-Rotation")
                    return True
                else:
                    print(f"当前选择: {current_selection}")
                    # 尝试切换到IP-Rotation
                    available_options = proxies[main_proxy_group].get('all', [])
                    if 'IP-Rotation' in available_options:
                        print("尝试切换到IP-Rotation...")
                        switch_response = requests.put(
                            f"http://127.0.0.1:9097/proxies/{main_proxy_group}",
                            json={"name": "IP-Rotation"},
                            timeout=5
                        )
                        if switch_response.status_code == 204:
                            print("✅ 成功切换到IP-Rotation")
                            return True
                        else:
                            print(f"❌ 切换失败: {switch_response.status_code}")
                            return False
                    else:
                        print("❌ IP-Rotation不在可选项中")
                        print(f"可选项: {', '.join(available_options)}")
                        return False
            else:
                print("❌ 未找到主代理组")
                return False
        else:
            print(f"获取代理信息失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"修复代理设置异常: {e}")
        return False

def test_after_fix():
    """修复后测试"""
    print("\n" + "=" * 60)
    print("修复后测试")
    print("=" * 60)
    
    import time
    print("等待2秒让设置生效...")
    time.sleep(2)
    
    try:
        proxy_config = {
            'http': 'http://127.0.0.1:7897',
            'https': 'http://127.0.0.1:7897'
        }
        
        # 测试几个不同的服务
        test_services = [
            ("httpbin", "http://httpbin.org/ip"),
            ("icanhazip", "https://icanhazip.com"),
        ]
        
        for name, url in test_services:
            try:
                print(f"\n测试 {name}...")
                response = requests.get(url, proxies=proxy_config, timeout=10, verify=False)
                if response.status_code == 200:
                    if name == "icanhazip":
                        ip = response.text.strip()
                    else:
                        data = response.json()
                        ip = data.get('origin', 'Unknown')
                    
                    print(f"  获取到的IP: {ip}")
                    
                    # 检查是否还是真实IP
                    if ip == "220.198.248.152":
                        print(f"  ❌ 仍然是真实IP")
                    else:
                        print(f"  ✅ 代理IP，代理工作正常！")
                        return True
                else:
                    print(f"  ❌ 状态码: {response.status_code}")
            except Exception as e:
                print(f"  ❌ 失败: {e}")
        
        return False
    except Exception as e:
        print(f"测试异常: {e}")
        return False

def main():
    print("Clash 路由检查和修复")
    print("=" * 60)
    
    # 检查当前代理选择
    proxy_ok = check_proxy_selection()
    
    if not proxy_ok:
        # 尝试修复
        fixed = fix_global_proxy()
        if fixed:
            # 修复后测试
            test_after_fix()
        else:
            print("\n❌ 无法自动修复，请手动检查Clash配置")
    else:
        # 即使代理选择正确，也测试一下
        test_after_fix()

if __name__ == "__main__":
    main()
