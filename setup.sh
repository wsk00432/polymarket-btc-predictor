#!/bin/bash
# Polymarket Maker Bot 安装脚本

set -e  # 遇到错误时退出

echo "🚀 开始安装 Polymarket Maker Bot..."

# 检查Python版本
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "Python版本: $PYTHON_VERSION"

if [[ "$PYTHON_VERSION" < "3.8" ]]; then
    echo "❌ 需要Python 3.8或更高版本"
    exit 1
fi

# 创建虚拟环境
echo "📦 创建虚拟环境..."
python3 -m venv venv

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 升级pip
echo "⬆️ 升级pip..."
pip install --upgrade pip

# 安装依赖
echo "📚 安装依赖包..."
pip install -r requirements.txt

# 创建配置文件
echo "⚙️ 创建配置文件..."
if [ ! -f .env ]; then
    echo "📝 创建 .env 文件..."
    cp .env.example .env
    echo "⚠️ 请编辑 .env 文件，填写你的配置信息"
fi

# 创建日志目录
echo "📁 创建日志目录..."
mkdir -p logs

# 创建数据库目录
echo "🗄️ 创建数据库目录..."
mkdir -p data

# 设置权限
echo "🔐 设置脚本权限..."
chmod +x run_bot.py
chmod +x phase1_quick_start.py

# 测试安装
echo "🧪 测试安装..."
python3 -c "import aiohttp; import asyncio; print('✅ 核心依赖安装成功')"

# 显示安装完成信息
echo ""
echo "🎉 安装完成！"
echo ""
echo "下一步："
echo "1. 编辑 .env 文件，填写你的配置信息"
echo "2. 运行: source venv/bin/activate"
echo "3. 启动机器人: python run_bot.py"
echo ""
echo "📋 配置说明："
echo "   • POLYMARKET_PRIVATE_KEY: 你的钱包私钥"
echo "   • POLYMARKET_WALLET_ADDRESS: 你的钱包地址"
echo "   • PAPER_TRADING: 建议先设置为 true 进行模拟交易"
echo ""
echo "🐝 祝你交易顺利！"