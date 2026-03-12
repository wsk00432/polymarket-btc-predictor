# Polymarket BTC Predictor 🐝

独立的Polymarket BTC价格预测系统，专注于比特币价格预测、Polymarket市场分析和自动化交易。

## 🎯 项目目标

### 核心使命
建立专注、可靠、可扩展的Polymarket BTC预测系统，实现自动化交易和风险管理。

### 关键特性
- **专注BTC预测**: 专注于比特币价格预测
- **Polymarket集成**: 连接Polymarket Gamma API
- **6551监控整合**: 集成现有监控功能
- **自动化交易**: BTC盈利系统
- **独立部署**: 可独立运行和扩展

## 📊 系统架构

### 技术栈
- **后端**: Python 3.9+, Flask, SQLite/PostgreSQL
- **数据源**: Binance API, Polymarket Gamma API
- **监控**: 6551-integration监控功能
- **部署**: Docker, 独立部署

### 核心模块
1. **Polymarket预测核心**: BTC价格预测算法
2. **数据收集器**: Polymarket API数据获取
3. **监控子系统**: 6551监控功能集成
4. **交易子系统**: 自动化交易引擎
5. **Web界面**: 实时监控仪表板

## 🚀 快速开始

### 1. 环境准备
```bash
# 克隆项目
git clone https://github.com/wsk00432/polymarket-btc-predictor.git
cd polymarket-btc-predictor

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置API密钥
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，填入您的API密钥
# 需要Binance API密钥和Polymarket访问权限
```

### 3. 启动系统
```bash
# 启动Polymarket预测服务
python polymarket_enhanced_service_fixed.py

# 启动监控脚本
./monitor_polymarket.sh

# 启动Web界面 (如果可用)
python web_api.py
```

### 4. 访问系统
- **预测服务**: 运行在后台，每15分钟生成预测
- **监控界面**: 查看系统状态和预测结果
- **日志文件**: `polymarket_service.log`

## 📈 核心功能

### BTC价格预测
- **15分钟预测**: 每15分钟生成BTC价格预测
- **技术指标**: RSI, MACD, 移动平均线等
- **准确率统计**: 实时跟踪预测准确性
- **24小时运行**: 不间断预测服务

### Polymarket市场分析
- **市场扫描**: 智能搜索BTC相关市场
- **机会评分**: 盈利机会评分系统 (0-100分)
- **交易计划**: 自动生成交易计划
- **风险管理**: 仓位大小和止损止盈设置

### 监控系统
- **系统健康**: 实时监控服务状态
- **性能指标**: CPU, 内存, 磁盘使用率
- **API可用性**: 外部API连接状态
- **错误告警**: 自动检测和通知问题

### 自动化交易
- **信号生成**: 基于预测生成交易信号
- **订单管理**: 自动化订单执行
- **风险控制**: 动态风险管理
- **性能跟踪**: 交易结果统计分析

## 🔧 配置说明

### 主要配置文件
- `.env` - 环境变量配置
- `config.py` - 系统配置
- `monitor_polymarket.sh` - 监控脚本

### 环境变量 (.env)
```bash
# Binance API配置
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here

# Polymarket配置
POLYMARKET_API_URL=https://gamma-api.polymarket.com

# 系统配置
PREDICTION_INTERVAL=900  # 预测间隔(秒)
LOG_LEVEL=INFO
DATA_DIR=./data
```

## 📊 性能指标

### 预测性能
- **预测频率**: 每15分钟
- **准确率目标**: > 60%
- **响应时间**: < 5秒
- **数据延迟**: < 10秒

### 系统资源
- **内存使用**: < 256MB
- **CPU使用**: < 20% (平均)
- **磁盘空间**: < 500MB
- **网络带宽**: < 1MB/小时

## 🔒 安全特性

### API安全
- API密钥环境变量管理
- 请求签名验证
- 访问频率限制
- 错误处理机制

### 数据安全
- 本地数据加密存储
- 敏感信息脱敏
- 访问日志记录
- 定期数据备份

## 🐳 容器化部署

### Docker部署
```bash
# 构建镜像
docker build -t polymarket-btc-predictor .

# 运行容器
docker run -d \
  --name polymarket-btc-predictor \
  --env-file .env \
  polymarket-btc-predictor
```

### 监控脚本
```bash
# 手动运行监控
./monitor_polymarket.sh

# 查看日志
tail -f polymarket_service.log
```

## 📡 系统接口

### 预测接口
- **每15分钟**: 自动生成BTC价格预测
- **预测验证**: 验证上一个预测的准确性
- **准确率统计**: 实时计算和更新准确率

### 监控接口
- **系统状态**: 服务运行状态检查
- **性能指标**: 资源使用情况
- **错误报告**: 问题检测和通知

### 数据接口
- **市场数据**: Polymarket市场信息
- **预测历史**: 历史预测记录
- **交易结果**: 自动化交易结果

## 🧪 测试

### 功能测试
```bash
# 运行基本测试
python test_basic.py

# 测试预测算法
python test_simulation.py

# 验证API连接
python test_api_integration.py
```

### 集成测试
```bash
# 运行端到端测试
python test_corrected_strategy.py

# 性能测试
python analyze_simulation_results.py
```

## 📈 监控和告警

### 内置监控
- 服务进程状态监控
- 预测准确率跟踪
- 系统资源使用监控
- API连接状态检查

### 告警机制
- 服务停止告警
- 预测准确率下降告警
- 系统资源告警
- API连接失败告警

### 监控脚本
`monitor_polymarket.sh` 脚本提供：
- 自动服务重启
- 状态检查
- 问题检测
- 日志记录

## 🤝 贡献指南

### 开发流程
1. Fork本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

### 代码规范
- 遵循PEP 8 Python代码规范
- 添加详细的文档字符串
- 编写单元测试
- 保持代码简洁清晰

### 提交信息规范
- feat: 新功能
- fix: 修复bug
- docs: 文档更新
- style: 代码格式调整
- refactor: 代码重构
- test: 测试相关
- chore: 构建过程或辅助工具变动

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- Polymarket团队提供的API支持
- Binance官方API
- 所有贡献者和用户
- 开源社区的支持

## 📞 支持

- 问题报告: [GitHub Issues](https://github.com/wsk00432/polymarket-btc-predictor/issues)
- 功能请求: [GitHub Discussions](https://github.com/wsk00432/polymarket-btc-predictor/discussions)

---

**开始您的Polymarket BTC预测之旅吧！** 🚀

**专注BTC预测，实现自动化交易！** 📊

_最后更新: 2026-03-12_