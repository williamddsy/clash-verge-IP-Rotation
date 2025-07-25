import requests
import time
import urllib3
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 代理配置
PROXY_CONFIG = {
    'http': 'http://127.0.0.1:7897',
    'https': 'http://127.0.0.1:7897'
}

# 全局变量
best_proxies = []  # 最佳节点列表
last_test_time = None  # 上次测试时间
proxy_performance = {}  # 节点性能数据

def get_all_proxies():
    """获取所有可用节点"""
    return [
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

def test_proxy_speed(proxy_name, timeout=8):
    """测试单个代理节点的速度"""
    try:
        # 切换到指定节点
        switch_response = requests.put(
            "http://127.0.0.1:9097/proxies/IP-Rotation",
            json={"name": proxy_name},
            timeout=5
        )

        if switch_response.status_code != 204:
            return proxy_name, float('inf'), "切换失败"

        # 等待切换生效
        time.sleep(1.5)

        # 测试速度
        start_time = time.time()
        response = requests.get(
            "http://httpbin.org/ip",
            proxies=PROXY_CONFIG,
            timeout=timeout,
            verify=False
        )
        end_time = time.time()

        if response.status_code == 200:
            response_time = end_time - start_time
            return proxy_name, response_time, "成功"
        else:
            return proxy_name, float('inf'), f"HTTP {response.status_code}"

    except Exception as e:
        return proxy_name, float('inf'), f"异常: {str(e)[:30]}"

def test_and_update_best_proxies():
    """测试所有节点并更新最佳节点列表"""
    global best_proxies, last_test_time, proxy_performance

    print(f"\n{'='*50}")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔍 开始测试节点速度...")
    print(f"{'='*50}")

    all_proxies = get_all_proxies()
    results = []

    # 并发测试所有节点
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_to_proxy = {
            executor.submit(test_proxy_speed, proxy): proxy
            for proxy in all_proxies
        }

        for future in as_completed(future_to_proxy):
            proxy_name, response_time, status = future.result()
            results.append((proxy_name, response_time, status))

            # 实时显示结果
            if response_time == float('inf'):
                print(f"  ❌ {proxy_name}: {status}")
            else:
                print(f"  ✅ {proxy_name}: {response_time:.3f}s")

    # 按响应时间排序，选择前10名
    results.sort(key=lambda x: x[1])

    best_proxies = []
    proxy_performance = {}

    print(f"\n🏆 前10名最佳节点:")
    for i, (proxy_name, response_time, status) in enumerate(results[:10]):
        if response_time != float('inf'):
            best_proxies.append(proxy_name)
            proxy_performance[proxy_name] = response_time
            print(f"  {i+1:2d}. {proxy_name}: {response_time:.3f}s")

    # 如果好节点不足10个，添加备用节点
    if len(best_proxies) < 10:
        for proxy_name, response_time, status in results[10:]:
            if len(best_proxies) >= 10:
                break
            if response_time != float('inf'):
                best_proxies.append(proxy_name)
                proxy_performance[proxy_name] = response_time
                print(f"  {len(best_proxies):2d}. {proxy_name}: {response_time:.3f}s (备用)")

    last_test_time = datetime.now()
    print(f"\n✅ 测试完成，选择了 {len(best_proxies)} 个最佳节点")
    next_test = last_test_time + timedelta(minutes=10)
    print(f"⏰ 下次测试时间: {next_test.strftime('%H:%M:%S')}")

def should_test_proxies():
    """判断是否需要重新测试节点"""
    if not last_test_time or not best_proxies:
        return True

    time_since_last_test = datetime.now() - last_test_time
    return time_since_last_test.total_seconds() >= 600  # 10分钟

def auto_rotate_ip():
    """智能自动轮换IP-Rotation组的节点"""
    global best_proxies

    print("🚀 启动智能IP轮换 (每10分钟测试速度，只使用最快的前10个节点)")

    index = 0
    
    index = 0
    while True:
        try:
            # 检查是否需要重新测试节点
            if should_test_proxies():
                test_and_update_best_proxies()

            # 如果没有可用的最佳节点，等待重新测试
            if not best_proxies:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️  没有可用节点，等待重新测试...")
                time.sleep(30)
                continue

            # 从最佳节点中选择下一个
            proxy = best_proxies[index % len(best_proxies)]

            # 切换节点
            response = requests.put(
                "http://127.0.0.1:9097/proxies/IP-Rotation",
                json={"name": proxy},
                timeout=5
            )

            if response.status_code == 204:
                # 显示节点性能信息
                performance = proxy_performance.get(proxy, "未知")
                if isinstance(performance, float):
                    perf_str = f"{performance:.3f}s"
                else:
                    perf_str = str(performance)

                print(f"[{datetime.now().strftime('%H:%M:%S')}] 切换到: {proxy} (响应时间: {perf_str})")
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 切换失败: {proxy} (状态码: {response.status_code})")

            index += 1
            time.sleep(5)

        except KeyboardInterrupt:
            print("\n👋 IP轮换已停止")
            break
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 运行异常: {str(e)}")
            time.sleep(10)

if __name__ == "__main__":
    auto_rotate_ip()
