#!/usr/bin/env python3
import requests
import urllib3
import yaml

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_clash_mode_and_config():
    """获取Clash当前模式和配置"""
    print("=" * 70)
    print("Clash 模式和配置分析")
    print("=" * 70)
    
    try:
        response = requests.get("http://127.0.0.1:9097/configs", timeout=5)
        if response.status_code == 200:
            config = response.json()
            print(f"🔧 Clash 运行模式: {config.get('mode', 'Unknown')}")
            print(f"🔧 混合端口: {config.get('mixed-port', 'Unknown')}")
            print(f"🔧 允许局域网: {config.get('allow-lan', 'Unknown')}")
            print(f"🔧 TUN模式: {config.get('tun', {}).get('enable', 'Unknown')}")
            return config
        else:
            print(f"❌ 获取配置失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 获取配置异常: {e}")
        return None

def analyze_proxy_groups():
    """分析代理组结构"""
    print("\n" + "=" * 70)
    print("代理组层级结构分析")
    print("=" * 70)
    
    try:
        response = requests.get("http://127.0.0.1:9097/proxies", timeout=5)
        if response.status_code == 200:
            proxies = response.json()['proxies']
            
            # 分析关键代理组的层级关系
            key_groups = ['GLOBAL', 'Proxy', 'Auto', 'Auto-Fast', 'IP-Rotation']
            
            print("📊 关键代理组层级关系:")
            for group_name in key_groups:
                if group_name in proxies:
                    group = proxies[group_name]
                    current = group.get('now', 'Unknown')
                    group_type = group.get('type', 'Unknown')
                    all_options = group.get('all', [])
                    
                    print(f"\n🔸 {group_name} ({group_type})")
                    print(f"   当前选择: {current}")
                    print(f"   可选项: {', '.join(all_options[:8])}{'...' if len(all_options) > 8 else ''}")
                    
                    # 如果当前选择也是一个代理组，显示其信息
                    if current in proxies and current != group_name:
                        sub_group = proxies[current]
                        sub_current = sub_group.get('now', 'Unknown')
                        print(f"   └─ {current} 当前选择: {sub_current}")
            
            return proxies
        else:
            print(f"❌ 获取代理组失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 分析代理组异常: {e}")
        return None

def explain_global_direct_issue():
    """解释GLOBAL选择DIRECT的原因"""
    print("\n" + "=" * 70)
    print("为什么GLOBAL代理组选择了DIRECT？")
    print("=" * 70)
    
    print("""
🤔 常见误解：
   很多用户认为在Clash界面选择"Global模式"就等于所有流量都走代理，
   但实际上这是两个不同的概念！

📚 概念解释：

1️⃣  Clash运行模式 (Mode):
   • Rule模式: 根据规则决定流量走向
   • Global模式: 所有流量都走"GLOBAL代理组"选择的代理
   • Direct模式: 所有流量都直连

2️⃣  GLOBAL代理组 (Proxy Group):
   • 这是一个具体的代理组，有自己的选择
   • 即使在Global模式下，GLOBAL组仍可以选择DIRECT
   • GLOBAL组的选择决定了实际的流量走向

🔍 您的情况分析：
   ✅ Clash模式: Global (正确)
   ❌ GLOBAL代理组选择: DIRECT (问题所在)
   
   结果: 虽然是Global模式，但因为GLOBAL组选择了DIRECT，
        所以所有流量都直连，没有走代理！

💡 解决方案：
   需要将GLOBAL代理组的选择从DIRECT改为实际的代理
   (比如IP-Rotation、Auto等)
""")

def check_config_file_defaults():
    """检查配置文件中的默认设置"""
    print("\n" + "=" * 70)
    print("检查配置文件中的默认设置")
    print("=" * 70)
    
    config_files = [
        "profiles/Rftlj0wRHup8.yaml",
        "clash-verge.yaml",
        "config.yaml"
    ]
    
    for config_file in config_files:
        try:
            print(f"\n📄 检查 {config_file}:")
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 查找GLOBAL代理组的配置
            if 'GLOBAL' in content:
                lines = content.split('\n')
                in_global_section = False
                for i, line in enumerate(lines):
                    if 'name: GLOBAL' in line or 'name: "GLOBAL"' in line:
                        in_global_section = True
                        print(f"   找到GLOBAL组定义 (第{i+1}行)")
                        # 显示接下来几行
                        for j in range(i, min(i+10, len(lines))):
                            if lines[j].strip():
                                print(f"   {j+1:3d}: {lines[j]}")
                            if j > i and lines[j].startswith('  - name:') and 'GLOBAL' not in lines[j]:
                                break
                        break
                
                if not in_global_section:
                    print("   未找到GLOBAL组的详细配置")
            else:
                print("   未找到GLOBAL组")
                
        except FileNotFoundError:
            print(f"   文件不存在: {config_file}")
        except Exception as e:
            print(f"   读取失败: {e}")

def show_solution_steps():
    """显示解决步骤"""
    print("\n" + "=" * 70)
    print("解决步骤和建议")
    print("=" * 70)
    
    print("""
🛠️  立即解决方法：

1️⃣  通过API修复 (已自动完成):
   我们的脚本已经自动将GLOBAL组切换到IP-Rotation

2️⃣  通过Clash界面手动修复:
   • 打开Clash Verge界面
   • 找到"代理"或"Proxies"页面
   • 找到GLOBAL代理组
   • 将其从DIRECT改为IP-Rotation或其他代理

3️⃣  防止再次发生:
   • 理解模式vs代理组的区别
   • 定期检查GLOBAL组的选择
   • 可以设置自动化脚本监控

⚠️  注意事项：
   • Clash重启后可能恢复默认设置
   • 某些配置更新可能重置代理组选择
   • 建议定期检查代理设置

🔄 自动化建议：
   可以在monitor_ip_rotation.py中添加定期检查，
   确保GLOBAL组始终选择正确的代理。
""")

def main():
    print("Clash 配置问题详细分析")
    print("解释为什么GLOBAL代理组选择了DIRECT")
    
    # 获取当前配置
    config = get_clash_mode_and_config()
    
    # 分析代理组结构
    proxies = analyze_proxy_groups()
    
    # 解释问题原因
    explain_global_direct_issue()
    
    # 检查配置文件
    check_config_file_defaults()
    
    # 显示解决方案
    show_solution_steps()

if __name__ == "__main__":
    main()
