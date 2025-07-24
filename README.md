# IP-Rotation 自动轮换代理

这是一个基于 Clash API 的自动 IP 轮换解决方案，可以定期切换代理节点来避免 IP 限制。

## 功能特性

- 🔄 自动轮换多个代理节点
- ⏰ 可配置切换间隔（默认5秒）
- 📊 实时监控节点切换状态
- 🛡️ 异常处理和错误重试
- 📝 详细的切换日志记录

## 文件说明

### 核心脚本
- `auto_rotate_ip.py` - 自动轮换IP的主脚本
- `monitor_ip_rotation.py` - 监控节点切换状态的脚本

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

### 2. 启动自动轮换
```bash
python auto_rotate_ip.py
```

### 3. 监控切换状态
```bash
python monitor_ip_rotation.py
```

## 使用方法

### 自动轮换模式
运行 `auto_rotate_ip.py` 会：
- 每5秒自动切换到下一个节点
- 按顺序循环使用所有配置的节点
- 显示切换日志和状态

示例输出：
```
[14:30:15] 切换到: GLaDOS-B1-01
[14:30:20] 切换到: GLaDOS-B1-02
[14:30:25] 切换到: GLaDOS-US-01
```

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

### 常见问题

**Q: 脚本提示"请求异常"**
A: 检查 Clash 是否运行，API 地址是否正确

**Q: 切换失败，返回非 204 状态码**
A: 检查节点名称是否正确，节点是否在配置文件中

**Q: 监控脚本显示"无法获取代理组信息"**
A: 确认已选择 IP-Rotation 代理组，且组名拼写正确

### 调试模式
在脚本中添加更详细的日志：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 许可证

MIT License