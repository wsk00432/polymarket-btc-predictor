# 🐝 Polymarket Maker Bot - 自动化做市机器人

基于2026年Polymarket新规则的自动化做市机器人，专注于5分钟BTC市场的高频做市策略。

## 🚀 核心特性

### 🔥 基于新规则优化
- **500ms延迟已取消** - 完全适配2026年2月18日新规则
- **动态taker手续费** - 手续费感知订单签名
- **maker优先策略** - 从taker套利转向maker流动性提供
- **极速循环** - 撤单/重下循环目标<100ms

### 💰 盈利模式
- **返佣收入** - maker订单获得手续费返佣
- **价格差利润** - 0.90-0.95美元挂单，结算获得0.05-0.10美元利润
- **5分钟市场** - 每天288个确定性机会
- **T-10秒策略** - 窗口结束前10秒，BTC方向已有85%确定性

### ⚡ 技术架构
- **WebSocket实时连接** - 不是REST轮询
- **手续费感知** - 所有订单包含feeRateBps字段
- **低延迟基础设施** - 要求网络延迟<5ms
- **自我优化** - 基于历史表现自动调整参数

## 📁 项目结构

```
polymarket-btc-predictor/
├── phase1_quick_start.py     # 核心机器人代码
├── run_bot.py               # 主运行脚本
├── config.py                # 配置文件
├── .env.example             # 环境变量示例
├── requirements.txt         # Python依赖
├── setup.sh                 # 安装脚本
├── README_MAKER_BOT.md      # 本文档
├── AUTOMATED_MAKER_BOT_PLAN.md  # 详细方案
└── logs/                    # 日志目录
```

## 🛠️ 快速开始

### 1. 安装依赖
```bash
# 运行安装脚本
chmod +x setup.sh
./setup.sh

# 或手动安装
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 配置环境变量
```bash
# 复制示例文件
cp .env.example .env

# 编辑 .env 文件，填写以下信息：
# - POLYMARKET_PRIVATE_KEY: 你的钱包私钥
# - POLYMARKET_WALLET_ADDRESS: 你的钱包地址
# - PAPER_TRADING: true (建议先模拟交易)
```

### 3. 启动机器人
```bash
# 激活虚拟环境
source venv/bin/activate

# 启动机器人
python run_bot.py
```

## 🎯 策略说明

### 5分钟市场策略
```
每天288个5分钟市场 (00:00, 00:05, 00:10, ..., 23:55)
每个市场窗口: 5分钟
执行时机: T-10秒 (窗口结束前10秒)
挂单价格: 0.90-0.95美元
预期利润: 0.05-0.10美元/合约 + 返佣
```

### T-10秒策略原理
根据文章研究，在5分钟窗口结束前10秒：
- BTC价格方向已有85%确定性
- 但Polymarket赔率尚未完全反映这一信息
- 此时挂maker单可获得优势价格

### 做市策略
- **双边挂单** - 在YES和NO两侧同时挂单
- **动态价差** - 根据市场波动调整买卖价差
- **快速刷新** - 价格变化时立即更新订单
- **风险控制** - 避免在50%概率区间过度做市

## ⚙️ 配置说明

### 关键配置项
```python
# config.py 中的关键配置

# 风险控制
MAX_POSITION_PER_MARKET = 1000      # 单市场最大仓位
MAX_DAILY_LOSS = 100                # 每日最大亏损(美元)

# 5分钟市场策略
T_MINUS_SECONDS = 10                # T-10秒执行
TARGET_PRICE_RANGE = (0.90, 0.95)   # 目标价格范围

# 性能目标
TARGET_CANCEL_REPLACE_MS = 100      # 撤单/重下循环目标
MAX_ACCEPTABLE_LATENCY_MS = 200     # 最大可接受延迟
```

### 环境变量 (.env)
```bash
# 必须配置
POLYMARKET_PRIVATE_KEY=your_private_key
POLYMARKET_WALLET_ADDRESS=0xYourAddress

# 建议配置
PAPER_TRADING=true                  # 模拟交易模式
LOG_LEVEL=INFO                      # 日志级别
```

## 📊 性能监控

### 关键指标
- **循环延迟** - 撤单/重下循环时间 (<100ms目标)
- **网络延迟** - VPS到交易所的延迟 (<5ms要求)
- **成交率** - 挂单成交比例 (>80%目标)
- **返佣收入** - maker返佣累计
- **错误率** - 异常错误比例 (<1%目标)

### 监控报告
机器人每分钟输出性能报告：
```
⚡ 性能报告 ⚡
时间: 2026-02-26 14:30:00
----------------------------
WebSocket消息: 1250
活跃订单: 8
撤单/重下循环:
  • 平均: 85.2ms
  • 最快: 62.1ms
  • 最慢: 112.5ms
  • 次数: 24
----------------------------
```

## 🚨 风险控制

### 必须避免的错误
1. ❌ 使用REST而不是WebSocket
2. ❌ 订单签名遗漏feeRateBps字段
3. ❌ 在家用Wi-Fi上运行
4. ❌ 硬编码手续费率
5. ❌ 在50%概率区间做市不考虑反向选择

### 风险控制措施
- **单市场仓位限制** - 防止过度集中
- **每日亏损限制** - 自动停止机制
- **价格滑点控制** - 最大可接受滑点
- **连接监控** - 自动重连机制
- **异常报警** - Telegram/邮件报警

## 🔄 自我优化

### 优化参数
```python
PARAMETERS_TO_OPTIMIZE = [
    'order_size',          # 订单大小
    'price_spread',        # 价格间隔
    'cancel_delay_ms',     # 撤单延迟
    'refresh_interval_ms', # 刷新间隔
]
```

### 优化目标
```python
OPTIMIZATION_WEIGHTS = {
    'profit': 0.4,        # 利润权重
    'fill_rate': 0.3,     # 成交率权重
    'rebate_income': 0.2, # 返佣收入权重
    'risk_score': -0.1,   # 风险分数权重(负值)
}
```

## 💻 部署要求

### 基础设施
- **机房VPS** - 网络延迟<5ms (不能用家用网络)
- **专用服务器** - 24/7稳定运行
- **静态IP** - 避免连接问题
- **监控系统** - 实时性能监控

### 推荐VPS配置
- **CPU**: 4+核心
- **内存**: 8GB+
- **网络**: 1Gbps+带宽
- **位置**: 靠近交易所服务器(新加坡/美国)

### 部署步骤
1. **测试环境** - 本地开发测试
2. **模拟交易** - 纸交易验证策略
3. **小规模实盘** - 最小资金测试
4. **逐步扩大** - 验证后增加资金

## 📈 预期收益

### 保守估计
```
每天288个5分钟市场
参与率: 50% (144个市场)
每个市场: 0.075美元利润 + 返佣
每日利润: 144 × 0.075 = 10.8美元
每月利润: 10.8 × 30 = 324美元
```

### 优化潜力
- **提高参与率**到80%: 518美元/月
- **增加仓位规模**: 线性扩展
- **多市场策略**: BTC + ETH + 其他
- **策略优化**: 机器学习优化参数

## 🐛 故障排除

### 常见问题
1. **连接失败**
   - 检查网络连接
   - 验证API密钥
   - 检查防火墙设置

2. **订单被拒绝**
   - 确认feeRateBps字段
   - 检查手续费率查询
   - 验证钱包余额

3. **延迟过高**
   - 切换到机房VPS
   - 优化网络路由
   - 减少并发请求

4. **策略不盈利**
   - 检查市场条件
   - 调整策略参数
   - 回测历史数据

### 调试模式
```bash
# 设置调试日志级别
export LOG_LEVEL=DEBUG

# 启用详细日志
python run_bot.py --debug
```

## 🔮 未来扩展

### 短期计划
1. **Rust版本** - 性能优化版本
2. **多交易所** - 集成更多数据源
3. **机器学习** - 预测模型优化

### 长期计划
1. **跨市场套利** - 多个预测市场
2. **组合策略** - 多种策略组合
3. **资产管理** - 自动资金分配

## 📚 参考资料

### 核心文章
- [Polymarket新规发布，如何构建一个新的交易机器人](https://www.theblockbeats.info/news/61326)
- [How to build a Polymarket bot (after new rules edition)](https://x.com/_dominatos/status/2024871493809680410)

### 技术文档
- [Polymarket API文档](https://docs.polymarket.com/)
- [CLOB API参考](https://clob.polymarket.com/docs)
- [Polygon网络文档](https://docs.polygon.technology/)

### 相关工具
- [polyfill-rs](https://github.com/polymarket/polyfill-rs) - Rust高性能库
- [polymarket-client-sdk](https://github.com/polymarket/polymarket-client-sdk) - 官方SDK
- [py-clob-client](https://pypi.org/project/py-clob-client/) - Python客户端

## 👥 贡献指南

### 开发流程
1. Fork项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

### 代码规范
- 遵循PEP 8规范
- 添加类型注解
- 编写单元测试
- 更新文档

### 测试要求
```bash
# 运行测试
pytest tests/

# 检查代码质量
flake8 .
mypy .
black --check .
```

## 📄 许可证

MIT License - 详见LICENSE文件

## 🆘 支持

- **问题反馈**: GitHub Issues
- **功能请求**: GitHub Discussions
- **紧急支持**: 创建Issue标记为urgent

---

**免责声明**: 本软件仅供学习和研究使用。加密货币交易具有高风险，可能导致资金损失。使用本软件前，请确保你了解相关风险，并只使用你能承受损失的资金进行交易。

*最后更新: 2026年2月26日*
*版本: 1.0.0*