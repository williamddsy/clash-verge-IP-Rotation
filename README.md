# IP-Rotation 自动轮换代理

这是一个基于 Clash API 的自动 IP 轮换解决方案，可以定期切换代理节点来避免 IP 限制。

## 功能特性

- 🔄 自动轮换多个代理节点
- ⏰ 可配置切换间隔（默认5秒）
- 📊 实时监控节点切换状态
- 🛡️ 异常处理和错误重试
- 📝 详细的切换日志记录
- 🔧 自动检测和修复代理配置问题
- 🚨 智能诊断工具集

## 文件说明

### 核心脚本
- `smart_rotate_ip.py` - 🚀 **智能轮换系统**（推荐使用）
  - 每10分钟自动测试所有节点网速
  - 只使用响应时间最快的前10个节点
  - 并发测试，实时显示性能数据
- `auto_rotate_ip.py` - 智能自动轮换IP的主脚本（已升级，包含速度测试）
- `monitor_ip_rotation.py` - 监控节点切换状态的脚本（已优化，包含自动修复功能）

### 诊断工具
- `diagnose_clash.py` - 全面诊断Clash API和代理连接状态
- `check_clash_routing.py` - 检查和自动修复代理路由配置
- `check_proxy_status.py` - 检查系统代理设置和连接状态
- `explain_clash_config.py` - 详细解释Clash配置问题
- `find_global_source.py` - 分析GLOBAL代理组来源

### 配置文件
- `profiles/Rftlj0wRHup8.yaml` - Clash 配置文件，包含 IP-Rotation 代理组

## 快速开始

### 1. 配置 Clash
确保 `profiles/Rftlj0wRHup8.yaml` 中包含 IP-Rotation 代理组：

```yaml
proxy-groups:
  - name: "IP-Rotation"
    type: select
    proxies:
      - GLaDOS-B1-01
      - GLaDOS-B1-02
      - GLaDOS-US-01
      # ... 更多节点
```

### 2. 启动智能轮换（推荐）
```bash
python smart_rotate_ip.py
```

### 3. 启动基础轮换
```bash
python auto_rotate_ip.py
```

### 4. 监控切换状态
```bash
python monitor_ip_rotation.py
```

## 🔧 问题诊断

如果遇到代理不工作的问题，可以使用以下诊断工具：

### 全面诊断
```bash
python diagnose_clash.py
```

### 检查代理路由
```bash
python check_clash_routing.py
```

### 检查系统代理
```bash
python check_proxy_status.py
```

## 使用方法

### 🚀 智能轮换模式（推荐）
运行 `smart_rotate_ip.py` 会：
- 启动时测试所有节点的网速
- 每10分钟重新测试，动态更新最佳节点列表
- 只使用响应时间最快的前10个节点进行轮换
- 每5秒切换到下一个最佳节点
- 显示详细的性能数据和切换日志

示例输出：
```
🚀 启动智能IP轮换系统
📊 每10分钟自动测试节点速度，只使用最快的前10个节点

🏆 前10名最佳节点:
   1. GLaDOS-B1-02: 0.234s
   2. GLaDOS-US-01: 0.267s
   3. GLaDOS-T3-03: 0.289s
   ...

[14:30:15] 切换到: GLaDOS-B1-02 (响应时间: 0.234s)
[14:30:20] 切换到: GLaDOS-US-01 (响应时间: 0.267s)
```

### 基础轮换模式
运行 `auto_rotate_ip.py` 会：
- 启动时测试所有节点，选择最快的前10个
- 每10分钟重新测试节点性能
- 按顺序循环使用最佳节点
- 显示切换日志和性能数据

### 监控模式
运行 `monitor_ip_rotation.py` 会：
- 实时监控当前使用的节点
- 记录节点切换事件
- 统计切换频率

示例输出：
```
[14:30:15] 初始节点: GLaDOS-B1-01
[14:30:20] 节点切换 #1: GLaDOS-B1-01 -> GLaDOS-B1-02 (运行5.0s)
[14:30:25] 节点切换 #2: GLaDOS-B1-02 -> GLaDOS-US-01 (运行10.0s)
```

## 配置说明

### API 配置
```python
CLASH_API_BASE = "http://127.0.0.1:9097"  # Clash API 地址
SECRET = ""  # API 密钥（如果设置了的话）
```

### 节点列表
在 `auto_rotate_ip.py` 中修改 `proxies` 列表来自定义轮换的节点：

```python
proxies = [
    "GLaDOS-B1-01", "GLaDOS-B1-02", "GLaDOS-B1-03",
    "GLaDOS-US-01", "GLaDOS-US-02",
    "GLaDOS-TW-01", "GLaDOS-TW-02",
    # 添加更多节点...
]
```

### 切换间隔
修改 `time.sleep(5)` 来调整切换间隔（秒）。

## 注意事项

1. **确保 Clash 运行**：脚本需要 Clash 在 `127.0.0.1:9097` 运行
2. **选择正确代理组**：在 Clash 界面中选择 `IP-Rotation` 代理组
3. **节点可用性**：确保配置的节点都是可用的
4. **API 权限**：如果 Clash 设置了 secret，需要在脚本中配置

## 故障排除

### 🚨 最新修复：GLOBAL代理组问题

**问题**：监控脚本显示真实IP而不是代理IP
**原因**：Clash的GLOBAL代理组默认选择了DIRECT，导致流量直连
**解决**：运行 `python monitor_ip_rotation.py`，脚本会自动检测并修复此问题

### 常见问题

**Q: 脚本提示"请求异常"**
A: 检查 Clash 是否运行，API 地址是否正确

**Q: 切换失败，返回非 204 状态码**
A: 检查节点名称是否正确，节点是否在配置文件中

**Q: 监控脚本显示"无法获取代理组信息"**
A: 确认已选择 IP-Rotation 代理组，且组名拼写正确

**Q: 获取的是真实IP而不是代理IP**
A: 运行 `python check_clash_routing.py` 检查GLOBAL代理组设置

**Q: SSL连接错误**
A: 已在新版本中修复，脚本会自动禁用SSL警告

### 诊断步骤

1. **全面诊断**：`python diagnose_clash.py`
2. **检查路由**：`python check_clash_routing.py`
3. **检查系统代理**：`python check_proxy_status.py`
4. **查看详细解释**：`python explain_clash_config.py`

### 调试模式
在脚本中添加更详细的日志：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 更新日志

### v2.1 (2025-01-25)
- 🚀 **新增智能IP轮换系统**
- 📊 每10分钟自动测试节点网速，只使用最快的前10个节点
- ⚡ 并发测试提高效率，避免慢节点拖累整体性能
- 📈 实时显示节点性能数据和响应时间
- 🎯 智能节点选择，大幅提升网络体验

### v2.0 (2025-01-25)
- 🔧 修复GLOBAL代理组默认选择DIRECT的问题
- 🚨 添加自动检测和修复功能
- 🛠️ 新增完整的诊断工具集
- 📝 优化错误处理和SSL兼容性
- 📊 改进监控脚本的稳定性

## 许可证

MIT License