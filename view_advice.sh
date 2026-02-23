#!/bin/bash
echo "🔍 最新 Polymarket 投资建议"
echo "📄 日志文件: /root/clawd/polymarket_advice.log"
echo "🕒 更新时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "📋 当前运行状态: $(if pgrep -f periodic_oi_advice.py > /dev/null; then echo "运行中"; else echo "已停止"; fi)"
echo "========================================="
echo ""

# 显示最新的投资建议（最后25行，以包含更多完整条目）
tail -25 /root/clawd/polymarket_advice.log

echo ""
echo "========================================="
echo "💡 说明:"
echo "   • 合约地址显示的是期货交易对，而非代币智能合约地址"
echo "   • 真实的代币合约地址通常不在此类交易对数据中提供"
echo "   • 如需具体代币合约地址，需通过其他途径查询"
echo "   • 投资有风险，请谨慎决策"
echo ""
echo "🔧 管理命令:"
echo "   • 查看完整日志: 'cat /root/clawd/polymarket_advice.log'"
echo "   • 实时监控: 'tail -f /root/clawd/polymarket_advice.log'"
echo "   • 停止服务: 'pkill -f periodic_oi_advice.py'"