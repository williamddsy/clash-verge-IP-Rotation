#!/usr/bin/env python3
import requests
import time
import threading
import urllib3
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Clash API 配置
CLASH_API_BASE = "http://127.0.0.1:9097"
SECRET = ""  # 如果设置了secret，在这里填入

# 代理配置
PROXY_CONFIG = {
    'http': 'http://127.0.0.1:7897',
    'https': 'http://127.0.0.1:7897'
}

class SmartIPRotator:
    def __init__(self):
        # 所有可用节点
        self.all_proxies = [
            # B1 系列
            "GLaDOS-B1-01", "GLaDOS-B1-02", "GLaDOS-B1-03", "GLaDOS-B1-04",
            "GLaDOS-B1-05", "GLaDOS-B1-06", "GLaDOS-B1-07", "GLaDOS-B1-08",
            
            # T3 系列
            "GLaDOS-T3-01", "GLaDOS-T3-02", "GLaDOS-T3-03", "GLaDOS-T3-04",
            "GLaDOS-T3-05", "GLaDOS-T3-06",
            
            # US 系列
            "GLaDOS-US-01", "GLaDOS-US-02", "GLaDOS-US-03", "GLaDOS-US-04",
            "GLaDOS-US-05", "GLaDOS-US-06",
            
            # TW 系列
            "GLaDOS-TW-01", "GLaDOS-TW-02", "GLaDOS-TW-03", "GLaDOS-TW-04",
            "GLaDOS-TW-05", "GLaDOS-TW-06",
            
            # JP 系列
            "GLaDOS-JP-01", "GLaDOS-JP-02", "GLaDOS-JP-03",
            
            # SG 系列
            "GLaDOS-SG-01", "GLaDOS-SG-02", "GLaDOS-SG-03",
            
            # HK 系列
            "GLaDOS-HK-01", "GLaDOS-HK-02", "GLaDOS-HK-03",
            
            # D1 系列
            "GLaDOS-D1-01", "GLaDOS-D1-02", "GLaDOS-D1-03"
        ]
        
        # 当前使用的最佳节点列表（前10名）
        self.best_proxies = []
        
        # 节点性能数据
        self.proxy_performance = {}
        
        # 上次测试时间
        self.last_test_time = None
        
        # 测试间隔（10分钟）
        self.test_interval = 600  # 秒
        
        # 轮换索引
        self.rotation_index = 0
        
        # 线程锁
        self.lock = threading.Lock()

    def test_proxy_speed(self, proxy_name, timeout=10):
        """测试单个代理节点的速度"""
        try:
            # 切换到指定节点
            switch_response = requests.put(
                f"{CLASH_API_BASE}/proxies/IP-Rotation",
                json={"name": proxy_name},
                timeout=5
            )
            
            if switch_response.status_code != 204:
                return proxy_name, float('inf'), "切换失败"
            
            # 等待切换生效
            time.sleep(2)
            
            # 测试速度 - 使用多个测试URL
            test_urls = [
                "http://httpbin.org/ip",
                "https://icanhazip.com",
                "https://ipinfo.io/ip"
            ]
            
            total_time = 0
            success_count = 0
            
            for url in test_urls:
                try:
                    start_time = time.time()
                    response = requests.get(
                        url, 
                        proxies=PROXY_CONFIG, 
                        timeout=timeout,
                        verify=False
                    )
                    end_time = time.time()
                    
                    if response.status_code == 200:
                        total_time += (end_time - start_time)
                        success_count += 1
                    
                except Exception:
                    continue
            
            if success_count == 0:
                return proxy_name, float('inf'), "连接失败"
            
            # 计算平均响应时间
            avg_time = total_time / success_count
            return proxy_name, avg_time, "成功"
            
        except Exception as e:
            return proxy_name, float('inf'), f"测试异常: {str(e)}"

    def test_all_proxies(self):
        """并发测试所有代理节点的速度"""
        print(f"\n{'='*60}")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 开始测试所有节点速度...")
        print(f"{'='*60}")
        
        results = []
        
        # 使用线程池并发测试
        with ThreadPoolExecutor(max_workers=5) as executor:
            # 提交所有测试任务
            future_to_proxy = {
                executor.submit(self.test_proxy_speed, proxy): proxy 
                for proxy in self.all_proxies
            }
            
            # 收集结果
            for future in as_completed(future_to_proxy):
                proxy_name, response_time, status = future.result()
                results.append((proxy_name, response_time, status))
                
                # 实时显示测试结果
                if response_time == float('inf'):
                    print(f"  ❌ {proxy_name}: {status}")
                else:
                    print(f"  ✅ {proxy_name}: {response_time:.3f}s")
        
        # 按响应时间排序
        results.sort(key=lambda x: x[1])
        
        # 更新最佳节点列表（前10名）
        with self.lock:
            self.best_proxies = []
            self.proxy_performance = {}
            
            print(f"\n🏆 前10名最佳节点:")
            for i, (proxy_name, response_time, status) in enumerate(results[:10]):
                if response_time != float('inf'):
                    self.best_proxies.append(proxy_name)
                    self.proxy_performance[proxy_name] = response_time
                    print(f"  {i+1:2d}. {proxy_name}: {response_time:.3f}s")
            
            # 如果好节点不足10个，添加一些备用节点
            if len(self.best_proxies) < 10:
                for proxy_name, response_time, status in results[10:]:
                    if len(self.best_proxies) >= 10:
                        break
                    if response_time != float('inf'):
                        self.best_proxies.append(proxy_name)
                        self.proxy_performance[proxy_name] = response_time
                        print(f"  {len(self.best_proxies):2d}. {proxy_name}: {response_time:.3f}s (备用)")
            
            self.last_test_time = datetime.now()
            print(f"\n✅ 测试完成，选择了 {len(self.best_proxies)} 个最佳节点")
            print(f"下次测试时间: {(self.last_test_time + timedelta(seconds=self.test_interval)).strftime('%H:%M:%S')}")

    def should_test_proxies(self):
        """判断是否需要重新测试节点"""
        if not self.last_test_time:
            return True
        
        if not self.best_proxies:
            return True
        
        time_since_last_test = datetime.now() - self.last_test_time
        return time_since_last_test.total_seconds() >= self.test_interval

    def get_next_proxy(self):
        """获取下一个要使用的代理节点"""
        with self.lock:
            if not self.best_proxies:
                return None
            
            proxy = self.best_proxies[self.rotation_index % len(self.best_proxies)]
            self.rotation_index += 1
            return proxy

    def switch_proxy(self, proxy_name):
        """切换到指定代理"""
        try:
            response = requests.put(
                f"{CLASH_API_BASE}/proxies/IP-Rotation",
                json={"name": proxy_name},
                timeout=5
            )
            
            if response.status_code == 204:
                performance = self.proxy_performance.get(proxy_name, "未知")
                if isinstance(performance, float):
                    performance_str = f"{performance:.3f}s"
                else:
                    performance_str = str(performance)
                
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 切换到: {proxy_name} (响应时间: {performance_str})")
                return True
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 切换失败: {proxy_name} (状态码: {response.status_code})")
                return False
                
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 切换异常: {proxy_name} ({str(e)})")
            return False

    def run(self):
        """运行智能IP轮换"""
        print("🚀 启动智能IP轮换系统")
        print("📊 每10分钟自动测试节点速度，只使用最快的前10个节点")
        print("⏰ 每5秒切换一次节点")
        
        while True:
            try:
                # 检查是否需要重新测试节点
                if self.should_test_proxies():
                    self.test_all_proxies()
                
                # 获取下一个代理节点
                next_proxy = self.get_next_proxy()
                if next_proxy:
                    self.switch_proxy(next_proxy)
                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] 没有可用的代理节点，等待重新测试...")
                    time.sleep(30)  # 等待30秒后重新测试
                    continue
                
                # 等待5秒后切换下一个节点
                time.sleep(5)
                
            except KeyboardInterrupt:
                print("\n👋 智能IP轮换已停止")
                break
            except Exception as e:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 运行异常: {str(e)}")
                time.sleep(10)

def main():
    rotator = SmartIPRotator()
    rotator.run()

if __name__ == "__main__":
    main()
