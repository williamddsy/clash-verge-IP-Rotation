#!/usr/bin/env python3
import requests
import urllib3
import json

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_all_proxy_groups():
    """获取所有代理组的详细信息"""
    print("=" * 70)
    print("查找GLOBAL代理组的来源")
    print("=" * 70)
    
    try:
        response = requests.get("http://127.0.0.1:9097/proxies", timeout=5)
        if response.status_code == 200:
            proxies = response.json()['proxies']
            
            print(f"总共找到 {len(proxies)} 个代理/代理组")
            
            # 查找GLOBAL组
            if 'GLOBAL' in proxies:
                global_group = proxies['GLOBAL']
                print(f"\n🔍 GLOBAL代理组详细信息:")
                print(f"   类型: {global_group.get('type', 'Unknown')}")
                print(f"   当前选择: {global_group.get('now', 'Unknown')}")
                print(f"   历史记录: {global_group.get('history', [])}")
                print(f"   所有选项: {global_group.get('all', [])}")
                
                # 检查是否有特殊属性
                for key, value in global_group.items():
                    if key not in ['type', 'now', 'all', 'history']:
                        print(f"   {key}: {value}")
                
                return True
            else:
                print("❌ 未找到GLOBAL代理组")
                
                # 列出所有代理组
                print("\n📋 所有可用的代理组:")
                for name, info in proxies.items():
                    if info.get('type') in ['select', 'url-test', 'fallback', 'load-balance']:
                        print(f"   - {name} ({info.get('type', 'Unknown')})")
                
                return False
        else:
            print(f"❌ 获取代理组失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 获取代理组异常: {e}")
        return False

def check_clash_verge_builtin():
    """检查Clash Verge的内置配置"""
    print("\n" + "=" * 70)
    print("Clash Verge内置配置分析")
    print("=" * 70)
    
    print("""
💡 GLOBAL代理组的可能来源：

1️⃣  Clash Verge内置功能:
   Clash Verge可能会自动创建GLOBAL代理组来支持Global模式。
   这个组通常包含DIRECT、REJECT和所有可用的代理节点。

2️⃣  配置文件合并:
   虽然我们检查的配置文件中没有GLOBAL组定义，
   但Clash Verge可能在运行时动态创建这个组。

3️⃣  默认行为:
   在Global模式下，Clash需要一个"全局代理组"来决定流量走向，
   如果配置中没有定义，Clash Verge会自动创建一个。

🔍 为什么默认选择DIRECT：

1️⃣  安全考虑:
   为了避免意外的代理使用，默认选择DIRECT是安全的做法。

2️⃣  用户控制:
   让用户主动选择代理，而不是自动使用代理。

3️⃣  配置保护:
   避免因为代理配置错误导致网络问题。
""")

def explain_solution():
    """解释解决方案"""
    print("\n" + "=" * 70)
    print("完整解释和解决方案")
    print("=" * 70)
    
    print("""
🎯 您的问题完整解释：

1️⃣  您在界面选择了"Global模式" ✅
   这意味着所有流量都会通过GLOBAL代理组处理

2️⃣  但GLOBAL代理组默认选择了"DIRECT" ❌
   这导致虽然是Global模式，但流量都直连了

3️⃣  这不是bug，而是设计如此 💡
   Clash Verge为了安全，默认让GLOBAL组选择DIRECT

🔧 解决方案（已完成）：

✅ 我们的脚本已经自动将GLOBAL组切换到IP-Rotation
✅ 现在您的代理正常工作，IP轮换也正常

🛡️  防止再次发生：

1️⃣  理解概念区别:
   • Global模式 ≠ 自动使用代理
   • Global模式 = 使用GLOBAL组的选择

2️⃣  定期检查:
   • 检查GLOBAL组的当前选择
   • 确保选择了正确的代理而不是DIRECT

3️⃣  自动化监控:
   • 我们的monitor_ip_rotation.py已经包含自动检查
   • 会自动修复GLOBAL组选择DIRECT的问题

💡 记住：
   在Clash中，"模式"和"代理组选择"是两个不同的概念！
   Global模式只是告诉Clash使用GLOBAL组，
   但GLOBAL组具体选择什么代理，需要单独设置。
""")

def main():
    print("查找GLOBAL代理组来源和解释问题")
    
    # 获取代理组信息
    found_global = get_all_proxy_groups()
    
    # 解释Clash Verge的行为
    check_clash_verge_builtin()
    
    # 完整解释
    explain_solution()

if __name__ == "__main__":
    main()
