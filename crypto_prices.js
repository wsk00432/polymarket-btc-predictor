const fetch = require('node-fetch');

async function getCryptoPrices() {
  try {
    // 获取主要加密货币价格
    const response = await fetch('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,binancecoin,solana,polkadot,cardano,dogecoin,shiba-inu,avalanche,tron&vs_currencies=usd&include_24hr_change=true');
    const data = await response.json();
    
    console.log('💰 Web3币圈主流币今日行情:');
    console.log('');
    
    const coins = [
      { name: 'Bitcoin (BTC)', id: 'bitcoin' },
      { name: 'Ethereum (ETH)', id: 'ethereum' },
      { name: 'Binance Coin (BNB)', id: 'binancecoin' },
      { name: 'Solana (SOL)', id: 'solana' },
      { name: 'Polkadot (DOT)', id: 'polkadot' },
      { name: 'Cardano (ADA)', id: 'cardano' },
      { name: 'Dogecoin (DOGE)', id: 'dogecoin' },
      { name: 'Shiba Inu (SHIB)', id: 'shiba-inu' },
      { name: 'Avalanche (AVAX)', id: 'avalanche' },
      { name: 'Tron (TRX)', id: 'tron' }
    ];
    
    coins.forEach(coin => {
      const priceData = data[coin.id];
      if (priceData) {
        const price = priceData.usd;
        const change = priceData.usd_24h_change ? priceData.usd_24h_change.toFixed(2) : 0;
        const changeStr = change >= 0 ? `+${change}%` : `${change}%`;
        const arrow = change >= 0 ? '📈' : '📉';
        console.log(`${arrow} ${coin.name}: $${price.toLocaleString()} (${changeStr})`);
      }
    });
    
    console.log('');
    console.log(`数据更新时间: ${new Date().toLocaleString('zh-CN')}`);
  } catch (error) {
    console.error('获取数据失败:', error);
  }
}

getCryptoPrices();