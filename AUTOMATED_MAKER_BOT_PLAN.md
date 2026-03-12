# Polymarket自动化Maker机器人方案
# 基于2026年新规则（500ms延迟取消 + 动态手续费）

## 核心原则
1. **做maker，不做taker** - 获得返佣而不是支付手续费
2. **WebSocket实时连接** - 不是REST轮询
3. **手续费感知** - 所有订单必须包含feeRateBps
4. **极速循环** - 撤单/重下控制在100ms以内

## 系统架构

### 1. 数据层
```
┌─────────────────────────────────────┐
│          外部数据源                  │
│  • Binance WebSocket (价格)         │
│  • Polymarket WebSocket (订单簿)    │
│  • Polymarket API (手续费查询)      │
└─────────────────────────────────────┘
                    │
┌─────────────────────────────────────┐
│          数据处理引擎                │
│  • 实时价格监控                     │
│  • 订单簿分析                       │
│  • 手续费计算                       │
│  • 市场状态评估                     │
└─────────────────────────────────────┘
```

### 2. 策略层
```
┌─────────────────────────────────────┐
│          5分钟市场策略               │
│  • 时间确定性市场 (每天288个)       │
│  • T-10秒预测 (85%确定性)           │
│  • 0.90-0.95美元挂maker单           │
│  • 利润: 0.05-0.10美元 + 返佣       │
└─────────────────────────────────────┘
                    │
┌─────────────────────────────────────┐
│          15分钟市场策略              │
│  • 更长的预测窗口                   │
│  • 更高的流动性                     │
│  • 更稳定的返佣                     │
└─────────────────────────────────────┘
```

### 3. 执行层
```
┌─────────────────────────────────────┐
│          订单管理引擎                │
│  • WebSocket连接管理               │
│  • 订单签名 (包含feeRateBps)        │
│  • 撤单/重下循环 (<100ms)           │
│  • 风险控制                        │
└─────────────────────────────────────┘
                    │
┌─────────────────────────────────────┐
│          性能监控                   │
│  • 延迟监控 (<5ms VPS)              │
│  • 成功率统计                       │
│  • 返佣跟踪                        │
│  • 自我优化算法                     │
└─────────────────────────────────────┘
```

## 技术栈选择

### 推荐方案 (基于文章建议)
1. **Rust生态** (性能最优)
   - `polyfill-rs` - 热路径零分配，SIMD JSON解析
   - `polymarket-client-sdk` - 官方Rust SDK
   - `polymarket-hft` - 完整HFT框架

2. **Python方案** (快速开发)
   - `py-clob-client` - 官方Python客户端
   - 需要额外优化性能

### 基础设施要求
- **机房VPS** - 网络延迟 <5ms (不能用家用Wi-Fi)
- **专用服务器** - 稳定连接，24/7运行
- **监控系统** - 实时性能监控

## 具体实现步骤

### 阶段1: 基础架构搭建 (1-2天)
1. 设置VPS环境 (机房，低延迟)
2. 安装Rust/Python环境
3. 配置Polymarket API密钥
4. 实现WebSocket连接

### 阶段2: 核心功能开发 (3-5天)
1. 实现手续费查询API集成
2. 开发订单签名系统 (包含feeRateBps)
3. 实现撤单/重下循环
4. 添加基础风险控制

### 阶段3: 策略实现 (2-3天)
1. 5分钟市场时间确定性算法
2. T-10秒预测逻辑
3. maker挂单策略
4. 返佣跟踪系统

### 阶段4: 优化和监控 (2-3天)
1. 性能优化 (目标<100ms循环)
2. 添加详细日志和监控
3. 实现自我优化算法
4. 添加异常处理

## 关键代码模块

### 1. WebSocket管理器
```rust
// 实时连接Polymarket订单簿
struct WebSocketManager {
    binance_ws: WebSocket,      // Binance价格流
    polymarket_ws: WebSocket,   // Polymarket订单簿
    fee_api: FeeApi,           // 手续费查询
}
```

### 2. 订单签名器
```rust
// 包含手续费感知的订单签名
struct OrderSigner {
    private_key: String,
    fee_rate_bps: u32,  // 必须包含
}

impl OrderSigner {
    fn sign_order(&self, order: Order) -> SignedOrder {
        // 必须包含feeRateBps字段
        let payload = OrderPayload {
            salt: generate_salt(),
            maker: self.address,
            token_id: order.token_id,
            maker_amount: order.maker_amount,
            taker_amount: order.taker_amount,
            fee_rate_bps: self.fee_rate_bps,  // 关键字段
        };
        // 签名逻辑...
    }
}
```

### 3. 撤单/重下循环
```rust
// 目标: <100ms完成整个循环
struct CancelReplaceLoop {
    last_price: f64,
    current_orders: Vec<OrderId>,
    external_price_source: PriceSource,
}

impl CancelReplaceLoop {
    async fn run_cycle(&mut self) -> Result<Duration> {
        let start = Instant::now();
        
        // 1. 检查价格变化
        let new_price = self.external_price_source.get_price().await?;
        
        if (new_price - self.last_price).abs() > THRESHOLD {
            // 2. 批量撤单
            self.cancel_all_orders().await?;
            
            // 3. 查询最新手续费
            let fee_rate = self.fee_api.get_fee_rate().await?;
            
            // 4. 重新挂单
            self.place_new_orders(new_price, fee_rate).await?;
            
            self.last_price = new_price;
        }
        
        let duration = start.elapsed();
        Ok(duration)
    }
}
```

### 4. 5分钟市场策略
```python
class FiveMinuteMarketStrategy:
    def __init__(self):
        self.market_schedule = self.generate_market_schedule()
    
    def generate_market_schedule(self):
        """生成每天288个5分钟市场的时间表"""
        markets = []
        for hour in range(24):
            for minute in range(0, 60, 5):
                market_time = datetime.time(hour, minute)
                market_id = f"btc-5min-{hour:02d}{minute:02d}"
                markets.append({
                    'time': market_time,
                    'id': market_id,
                    'window_end': market_time + timedelta(minutes=5)
                })
        return markets
    
    async def execute_at_t_minus_10(self, market):
        """在窗口结束前10秒执行"""
        # 此时BTC方向已有85%确定性
        # 但Polymarket赔率尚未完全反映
        
        # 1. 分析当前BTC价格趋势
        direction = self.analyze_btc_direction()
        
        # 2. 在胜率更高的一侧挂maker单
        if direction == "UP":
            price = 0.92  # 0.90-0.95美元范围
            side = "YES"
        else:
            price = 0.92
            side = "NO"
        
        # 3. 挂单
        await self.place_maker_order(
            market_id=market['id'],
            side=side,
            price=price,
            amount=100  # 合约数量
        )
```

## 风险控制

### 1. 手续费风险
- 永远不要硬编码手续费率
- 每次下单前查询最新费率
- 监控手续费变化

### 2. 延迟风险
- 实时监控网络延迟
- 设置延迟阈值 (超过200ms报警)
- 备用VPS切换机制

### 3. 资金风险
- 单市场最大仓位限制
- 每日最大亏损限制
- 自动停止机制

### 4. 策略风险
- 避免在接近50%概率区间做市
- 监控反向选择风险
- 定期回测策略效果

## 自我完善机制

### 1. 性能学习
```python
class SelfOptimizer:
    def __init__(self):
        self.performance_history = []
        self.parameter_space = {
            'cancel_delay': [50, 100, 150],  # ms
            'order_size': [50, 100, 200],    # 合约数量
            'price_spread': [0.01, 0.02, 0.03],  # 价格间隔
        }
    
    def optimize_parameters(self):
        """基于历史表现优化参数"""
        best_params = None
        best_score = -float('inf')
        
        for params in self.generate_parameter_combinations():
            score = self.evaluate_parameters(params)
            if score > best_score:
                best_score = score
                best_params = params
        
        return best_params
    
    def evaluate_parameters(self, params):
        """评估参数组合的表现"""
        # 考虑因素:
        # 1. 返佣收入
        # 2. 成交率
        # 3. 滑点成本
        # 4. 风险调整后收益
        score = (params['rebate_income'] * 0.4 +
                 params['fill_rate'] * 0.3 -
                 params['slippage_cost'] * 0.2 -
                 params['risk_score'] * 0.1)
        return score
```

### 2. 市场适应
- 动态调整策略参数
- 学习市场模式变化
- 适应不同流动性环境

### 3. 错误恢复
- 自动重连机制
- 状态恢复系统
- 安全模式切换

## 部署和监控

### 1. 部署要求
- 专用VPS (推荐: AWS/GCP/Azure)
- 静态IP地址
- 99.9%可用性保证
- 自动备份系统

### 2. 监控指标
```
关键指标:
• 循环延迟: <100ms (目标)
• 网络延迟: <5ms (VPS到交易所)
• 成交率: >80% (目标)
• 返佣收入: 每日跟踪
• 错误率: <1% (目标)
```

### 3. 报警系统
- 延迟超过阈值
- 连接断开
- 异常错误率
- 资金异常变动

## 预期收益

### 保守估计 (基于文章分析)
- **5分钟市场**: 每天288个机会
- **每个机会**: 0.05-0.10美元利润 + 返佣
- **每日机会**: 假设参与50%的市场
- **每日利润**: 144个市场 × 0.075美元 = 10.8美元
- **月利润**: 10.8美元 × 30 = 324美元

### 优化后潜力
- 提高参与率到80%: 518.4美元/月
- 增加仓位规模: 可线性扩展
- 多市场策略: BTC + ETH + 其他

## 下一步行动

### 立即开始
1. [ ] 选择合适的VPS提供商
2. [ ] 设置开发环境
3. [ ] 获取Polymarket API访问
4. [ ] 实现基础WebSocket连接

### 短期目标 (1周内)
1. [ ] 完成核心架构
2. [ ] 实现基本maker功能
3. [ ] 测试5分钟市场策略
4. [ ] 部署到测试环境

### 中期目标 (2-3周)
1. [ ] 优化性能到<100ms
2. [ ] 实现自我优化算法
3. [ ] 添加完整监控
4. [ ] 实盘测试

### 长期目标 (1个月后)
1. [ ] 扩展到多个市场
2. [ ] 实现高级策略
3. [ ] 建立冗余系统
4. [ ] 自动化部署流水线

## 注意事项

### 必须避免的错误
1. ❌ 使用REST而不是WebSocket
2. ❌ 订单签名中遗漏feeRateBps
3. ❌ 在家用Wi-Fi上运行
4. ❌ 硬编码手续费率
5. ❌ 在50%概率区间做市不考虑反向选择

### 成功关键
1. ✅ 低延迟基础设施
2. ✅ 正确的手续费处理
3. ✅ 快速的撤单/重下循环
4. ✅ maker策略而不是taker
5. ✅ 持续的自我优化

---

*基于Polymarket新规则 (2026年2月18日生效)*  
*500ms延迟取消 + 动态taker手续费*  
*优势从taker套利转向maker流动性提供*