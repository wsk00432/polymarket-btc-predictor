"""
Polymarket Maker Bot 配置文件
"""

# ==================== 基础配置 ====================
# 注意：在生产环境中，这些敏感信息应该从环境变量或安全存储中读取

# 钱包配置
WALLET_CONFIG = {
    # 私钥（从环境变量读取）
    'private_key': '',  # 留空，从环境变量读取
    'wallet_address': '',  # 留空，从环境变量读取
    
    # 网络配置
    'rpc_url': 'https://polygon-rpc.com',  # Polygon主网
    'chain_id': 137,  # Polygon链ID
}

# API配置
API_CONFIG = {
    'polymarket_base_url': 'https://clob.polymarket.com',
    'polymarket_gamma_url': 'https://gamma-api.polymarket.com',
    'binance_ws_url': 'wss://stream.binance.com:9443/ws',
    'timeout': 10,  # 请求超时时间（秒）
    'retry_attempts': 3,  # 重试次数
}

# ==================== 交易配置 ====================
TRADING_CONFIG = {
    # 风险控制
    'max_position_per_market': 1000,  # 单市场最大仓位（合约数量）
    'max_daily_loss': 100,  # 每日最大亏损（美元）
    'max_slippage': 0.01,  # 最大滑点（1%）
    
    # 订单配置
    'default_order_size': 100,  # 默认订单大小（合约数量）
    'min_order_size': 10,  # 最小订单大小
    'order_expiry_hours': 1,  # 订单过期时间（小时）
    
    # 价格配置
    'price_precision': 4,  # 价格精度（小数点后位数）
    'min_price_increment': 0.0001,  # 最小价格变动
}

# ==================== 策略配置 ====================
STRATEGY_CONFIG = {
    # 5分钟市场策略
    'five_minute_markets': {
        'enabled': True,
        't_minus_seconds': 10,  # T-10秒执行
        'target_price_range': (0.90, 0.95),  # 目标价格范围
        'default_amount': 100,  # 默认合约数量
        'max_markets_per_hour': 12,  # 每小时最多参与的市场数
    },
    
    # 15分钟市场策略
    'fifteen_minute_markets': {
        'enabled': False,  # 暂时禁用
        't_minus_seconds': 30,
        'target_price_range': (0.85, 0.90),
        'default_amount': 200,
    },
    
    # 做市策略
    'market_making': {
        'enabled': True,
        'spread': 0.02,  # 买卖价差（2%）
        'depth': 3,  # 订单簿深度
        'refresh_interval_ms': 100,  # 刷新间隔（毫秒）
        'cancel_replace_threshold': 0.005,  # 价格变动阈值（0.5%）
    },
}

# ==================== 性能配置 ====================
PERFORMANCE_CONFIG = {
    # 延迟目标
    'target_cancel_replace_ms': 100,  # 撤单/重下循环目标（毫秒）
    'max_acceptable_latency_ms': 200,  # 最大可接受延迟
    'websocket_timeout_ms': 5000,  # WebSocket超时时间
    
    # 监控配置
    'stats_report_interval_sec': 60,  # 统计报告间隔（秒）
    'health_check_interval_sec': 30,  # 健康检查间隔
    'error_report_threshold': 5,  # 错误报告阈值
}

# ==================== 日志配置 ====================
LOGGING_CONFIG = {
    'level': 'INFO',  # 日志级别：DEBUG, INFO, WARNING, ERROR
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file_path': 'polymarket_maker.log',
    'max_file_size_mb': 10,  # 最大日志文件大小（MB）
    'backup_count': 5,  # 备份文件数量
}

# ==================== 自我优化配置 ====================
SELF_OPTIMIZATION_CONFIG = {
    'enabled': True,
    'learning_rate': 0.1,  # 学习率
    'exploration_rate': 0.05,  # 探索率
    'memory_size': 1000,  # 记忆大小
    
    # 优化参数
    'parameters_to_optimize': [
        'order_size',
        'price_spread',
        'cancel_delay_ms',
        'refresh_interval_ms',
    ],
    
    # 优化目标权重
    'optimization_weights': {
        'profit': 0.4,  # 利润权重
        'fill_rate': 0.3,  # 成交率权重
        'rebate_income': 0.2,  # 返佣收入权重
        'risk_score': -0.1,  # 风险分数权重（负值）
    },
}

# ==================== 市场过滤器 ====================
MARKET_FILTERS = {
    # 最小流动性要求
    'min_liquidity_usd': 1000,
    
    # 最小交易量要求
    'min_volume_usd': 5000,
    
    # 价格范围过滤
    'min_price': 0.05,  # 最低价格
    'max_price': 0.95,  # 最高价格
    
    # 排除的市场
    'excluded_categories': [
        'sports',  # 体育
        'politics',  # 政治
        'entertainment',  # 娱乐
    ],
    
    # 优先交易的市场
    'preferred_categories': [
        'crypto',  # 加密货币
        'finance',  # 金融
        'technology',  # 科技
    ],
}

# ==================== 手续费配置 ====================
FEE_CONFIG = {
    # 默认手续费率（基点）
    'default_fee_rate_bps': 150,  # 1.5%
    
    # 手续费查询
    'fee_query_interval_sec': 300,  # 手续费查询间隔（秒）
    'cache_duration_sec': 600,  # 缓存持续时间
    
    # 返佣配置
    'rebate_rate_bps': 50,  # 0.5%返佣（maker）
    'track_rebates': True,  # 跟踪返佣
}

# ==================== 网络配置 ====================
NETWORK_CONFIG = {
    # 代理配置（如果需要）
    'use_proxy': False,
    'proxy_url': '',
    
    # 连接池配置
    'max_connections': 100,
    'max_keepalive_connections': 20,
    
    # 重试配置
    'backoff_factor': 0.5,
    'status_forcelist': [500, 502, 503, 504],
}

# ==================== 数据库配置 ====================
DATABASE_CONFIG = {
    'enabled': True,
    'type': 'sqlite',  # sqlite, postgres, mysql
    'path': 'polymarket_bot.db',
    
    # 表配置
    'tables': {
        'orders': 'orders',
        'trades': 'trades',
        'performance': 'performance',
        'errors': 'errors',
    },
    
    # 保留时间
    'retention_days': {
        'orders': 30,
        'trades': 90,
        'performance': 180,
        'errors': 90,
    },
}

# ==================== 报警配置 ====================
ALERT_CONFIG = {
    'enabled': True,
    
    # 延迟报警
    'latency_alerts': {
        'threshold_ms': 200,
        'cooldown_minutes': 5,
    },
    
    # 错误报警
    'error_alerts': {
        'threshold_count': 10,
        'time_window_minutes': 5,
    },
    
    # 资金报警
    'balance_alerts': {
        'low_balance_threshold': 50,  # 美元
        'large_withdrawal_threshold': 1000,  # 美元
    },
    
    # 策略报警
    'strategy_alerts': {
        'consecutive_losses': 5,
        'daily_loss_threshold': 50,  # 美元
    },
}

# ==================== 测试配置 ====================
TESTING_CONFIG = {
    'paper_trading': True,  # 模拟交易
    'initial_balance': 1000,  # 初始余额（美元）
    'test_markets': ['btc-5min-test'],  # 测试市场
    'simulate_latency': True,  # 模拟延迟
    'latency_ms': 50,  # 模拟延迟毫秒数
}