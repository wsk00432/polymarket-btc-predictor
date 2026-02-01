# SSH隧道访问指南

## 如何通过SSH隧道安全访问币安持仓量激增检测雷达

当直接访问服务器端口受阻时，SSH隧道是最可靠的访问方式。

### Windows用户

1. **使用PuTTY**：
   - 下载并打开PuTTY
   - 在"Host Name"字段输入您的服务器IP：`43.167.222.200`
   - 在左侧导航栏中，展开"Connection" → "SSH" → "Tunnels"
   - 在"Source port"输入：`8080`
   - 在"Destination"输入：`localhost:8080`
   - 选择"Local ports accept connections from other hosts"
   - 点击"Add"按钮
   - 返回"Session"，点击"Open"建立连接

2. **使用Windows Terminal/MobaXterm**：
   ```bash
   ssh -L 8080:localhost:8080 username@43.167.222.200
   ```

### Mac/Linux用户

1. **打开终端并运行**：
   ```bash
   ssh -L 8080:localhost:8080 username@43.167.222.200
   ```

2. **如果希望后台运行**：
   ```bash
   ssh -f -N -L 8080:localhost:8080 username@43.167.222.200
   ```

### 访问应用

建立SSH隧道后，在您的本地浏览器中访问：
- Web界面：http://localhost:8080/
- API状态：http://localhost:8080/api/status

### 注意事项

- SSH隧道会在您断开SSH连接时关闭，如果需要持久连接，可以使用`autossh`工具
- SSH隧道是加密的，比直接访问更安全
- 此方法绕过了任何服务器端的防火墙或网络安全组限制

### 服务器状态

服务正在服务器上正常运行：
- 后端应用：localhost:8080 (服务器内部)
- Caddy反向代理：端口80和443 (服务器外部)

所有功能均正常，只是外部网络策略阻止了直接访问。