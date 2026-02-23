# ClawFeed × BTC Predictor 整合方案

> **整合目标**: 结合 ClawFeed 的新闻聚合能力和 BTC Predictor 的预测能力，打造更智能的交易决策系统

---

## 🎯 整合目标

1. **新闻情绪增强**: 使用 ClawFeed 收集加密相关新闻，作为 BTC 预测的情绪输入
2. **智能摘要输出**: 使用 ClawFeed 格式输出 BTC 预测的定期摘要（4H/日/周/月）
3. **架构改进**: 学习 ClawFeed 的设计模式改进我们的系统
4. **统一 API**: 提供一致的 REST API 接口
5. **Web 仪表板**: 创建统一的监控和管理界面

---

## 📋 整合阶段

### 阶段 1: 新闻情绪增强 (1-2 天)

**目标**: 将 ClawFeed 的新闻数据集成到 BTC 预测系统

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   ClawFeed      │────▶│  新闻情绪分析器   │────▶│  BTC Predictor  │
│  新闻聚合引擎    │     │  (新增模块)       │     │   预测引擎       │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

**新增文件**:
- `news_sentiment_analyzer.py` - 新闻情绪分析模块
- `clawfeed_integration.py` - ClawFeed API 客户端
- `crypto_news_sources.json` - 加密货币相关新闻源配置

**功能**:
- 从 ClawFeed 获取加密相关新闻
- 分析新闻情绪（正面/负面/中性）
- 将情绪分数传递给预测引擎
- 权重配置：新闻情绪占整体情绪的 30-50%

---

### 阶段 2: 智能摘要输出 (1-2 天)

**目标**: 实现多频率预测摘要输出

**新增文件**:
- `digest_generator.py` - 摘要生成器
- `digest_templates/` - 摘要模板目录
  - `4h_digest.md` - 4 小时摘要模板
  - `daily_digest.md` - 每日摘要模板
  - `weekly_digest.md` - 每周摘要模板
  - `monthly_digest.md` - 每月摘要模板

**功能**:
- 4 小时摘要：最近 120 次预测的统计分析
- 每日摘要：当日预测准确率 + 关键洞察
- 每周摘要：周度趋势分析 + 策略调整总结
- 每月摘要：月度表现报告 + 学习成果

**输出格式**:
- Markdown 文档
- RSS Feed
- JSON Feed
- Telegram 消息

---

### 阶段 3: 架构改进 (2-3 天)

**目标**: 学习 ClawFeed 的架构设计改进我们的系统

**改进点**:

#### 3.1 API 重构
```
当前:
- web_api.py (单一文件，功能有限)

改进后:
- api/
  - __init__.py
  - routes/
    - predictions.py
    - outcomes.py
    - digests.py
    - stats.py
  - middleware/
    - auth.py
    - rate_limit.py
  - models/
    - prediction.py
    - outcome.py
```

#### 3.2 数据库升级
```
当前:
- JSON 文件存储 (prediction_outcomes.json)

改进后:
- SQLite 数据库 (predictions.db)
- 表结构:
  - predictions (预测记录)
  - outcomes (评估结果)
  - performance_logs (性能日志)
  - strategy_configs (策略配置)
  - digests (摘要记录)
```

#### 3.3 配置系统
```
当前:
- 硬编码配置

改进后:
- config/
  - default.yaml
  - production.yaml
  - .env (环境变量)
```

---

### 阶段 4: Web 仪表板 (3-5 天)

**目标**: 创建统一的 Web 监控界面

**技术栈**:
- 前端：React/Vue + TailwindCSS
- 后端：Flask API (现有)
- 图表：Chart.js 或 Recharts

**功能模块**:
1. **实时预测面板**
   - 最新预测
   - 置信度趋势
   - 价格走势图

2. **准确率统计**
   - 总体准确率
   - 近期准确率趋势
   - 方向特定准确率

3. **摘要浏览**
   - 4H/日/周/月摘要列表
   - 摘要详情查看
   - RSS 订阅

4. **系统监控**
   - 服务健康状态
   - 预测生成频率
   - 评估服务状态

5. **配置管理**
   - 策略权重调整
   - 新闻源管理
   - 评估窗口配置

---

## 📁 新增目录结构

```
polymarket-btc-predictor/
├── api/                          # 新增：API 模块化
│   ├── __init__.py
│   ├── routes/
│   └── middleware/
├── config/                       # 新增：配置管理
│   ├── default.yaml
│   └── production.yaml
├── digest_templates/             # 新增：摘要模板
│   ├── 4h_digest.md
│   ├── daily_digest.md
│   └── weekly_digest.md
├── news_sources/                 # 新增：新闻源配置
│   └── crypto_news_sources.json
├── database/                     # 新增：数据库相关
│   ├── models.py
│   └── migrations/
├── web_dashboard/                # 新增：Web 前端
│   ├── src/
│   ├── public/
│   └── package.json
├── integrations/                 # 新增：外部集成
│   ├── clawfeed_client.py
│   └── news_sentiment_analyzer.py
├── tests/                        # 新增：测试套件
│   ├── unit/
│   └── e2e/
├── btc_predictor.py              # 改进：核心引擎
├── prediction_manager.py         # 改进：预测管理
├── periodic_evaluation.py        # 改进：评估服务
├── digest_generator.py           # 新增：摘要生成
├── web_api.py                    # 改进：API 入口
└── README.md                     # 改进：文档
```

---

## 🔧 实施步骤

### 第 1 步：克隆 ClawFeed 参考实现
```bash
cd /root/clawd/projects
git clone https://github.com/kevinho/clawfeed.git clawfeed-reference
```

### 第 2 步：创建整合分支
```bash
cd /root/clawd/projects/polymarket-btc-predictor
git checkout -b feature/clawfeed-integration
```

### 第 3 步：实现新闻情绪分析器
- 创建 `integrations/clawfeed_client.py`
- 实现新闻获取和情绪分析
- 集成到 `btc_predictor.py`

### 第 4 步：实现摘要生成器
- 创建 `digest_generator.py`
- 设计摘要模板
- 设置定时生成任务

### 第 5 步：数据库升级
- 设计 SQLite schema
- 创建迁移脚本
- 数据迁移（JSON → SQLite）

### 第 6 步：API 重构
- 模块化路由
- 添加认证中间件
- 实现速率限制

### 第 7 步：Web 仪表板开发
- 搭建前端框架
- 实现各功能模块
- 连接后端 API

### 第 8 步：测试与优化
- 单元测试
- E2E 测试
- 性能优化

### 第 9 步：文档更新
- 更新 README
- 编写 API 文档
- 创建使用指南

### 第 10 步：部署上线
- 配置生产环境
- 设置监控告警
- 推送 GitHub

---

## 📊 预期收益

| 指标 | 当前 | 整合后 | 提升 |
|------|------|--------|------|
| **预测准确率** | 60% | 65-70% | +5-10% |
| **数据源** | 1 (Binance) | 3+ (Binance + 新闻 + 社交媒体) | +200% |
| **输出频率** | 实时预测 | 实时 + 4H/日/周/月摘要 | +5 种 |
| **API 端点** | 5 个 | 20+ 个 | +300% |
| **用户界面** | 无 | Web 仪表板 | 新增 |
| **测试覆盖** | 0% | 60%+ | +60% |

---

## 🎯 立即开始

帮主，我可以现在开始实施整合方案。建议顺序：

1. **先实现新闻情绪分析器** (最快见效)
2. **然后实现摘要生成器** (提升用户体验)
3. **最后进行架构升级** (长期维护性)

您想从哪个开始？或者我按顺序全部实施？
