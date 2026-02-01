# 持久化访问解决方案

## 问题
腾讯云Web终端会定时断开连接，导致无法持续访问Clawdbot服务。

## 解决方案：使用tmux创建持久化会话

### 1. 启动持久化会话
```bash
# 安装tmux（如果未安装）
yum install -y tmux || apt-get install -y tmux

# 创建名为"clawdbot"的持久化会话
tmux new-session -d -s clawdbot

# 在会话中启动clawdbot
tmux send-keys -t clawdbot 'export NODE_OPTIONS="--dns-result-order=ipv4first" && clawdbot gateway --bind loopback --port 18789 --verbose --force' Enter

# 您可以随时附加到会话查看状态
tmux attach -t clawdbot
```

### 2. 保持会话持久化
即使SSH连接断开，tmux会话仍会继续运行。

### 3. 重新连接步骤
当Web终端断开后：
1. 重新登录腾讯云Web终端
2. 运行 `tmux attach -t clawdbot` 重新连接到Clawdbot会话
3. 如果需要在后台运行，按 Ctrl+B 然后按 D 键分离会话

### 4. 检查会话状态
```bash
tmux list-sessions
```

### 5. 其他持久化选项
您也可以考虑：
- 使用SSH客户端（如PuTTY、Terminal等）直接连接服务器，比Web终端更稳定
- 设置SSH密钥认证，避免每次输入密码
- 配置SSH心跳保持连接：在SSH客户端添加 `ServerAliveInterval 60`

### 6. 服务器重启后的自动启动
要实现服务器重启后自动启动Clawdbot，可以创建一个系统服务或使用crontab：
```bash
# 添加到crontab实现开机启动
crontab -l
# 添加这一行（使用crontab -e编辑）：
@reboot export NODE_OPTIONS="--dns-result-order=ipv4first" && clawdbot gateway --bind loopback --port 18789 --verbose --force
```