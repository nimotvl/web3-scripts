#!/usr/bin/env python3
"""
PAPER TRADE SYSTEM v1.0
- Simulasi trading tanpa real money
- Track portfolio, P&L, win rate
- Support multi-chain price feed
"""

import json
import os
import time
import requests
from datetime import datetime
from pathlib import Path

DATA_DIR = Path.home() / ".hermes" / "paper_trade"
DATA_DIR.mkdir(parents=True, exist_ok=True)

PORTFOLIO_FILE = DATA_DIR / "portfolio.json"
TRADES_FILE = DATA_DIR / "trades.json"
CONFIG_FILE = DATA_DIR / "config.json"

# Default config
DEFAULT_CONFIG = {
    "initial_balance": 10000,  # USD
    "currency": "USD",
    "fee_percent": 0.1,  # 0.1% per trade
    "slippage_percent": 0.05,  # 0.05% slippage simulation
}

# Price API (CoinGecko free)
COINGECKO_API = "https://api.coingecko.com/api/v3"

def load_json(file, default):
    if file.exists():
        return json.loads(file.read_text())
    return default

def save_json(file, data):
    file.write_text(json.dumps(data, indent=2, default=str))

def get_price(symbol):
    """Get current price from CoinGecko"""
    symbol = symbol.lower()
    # Map common symbols
    symbol_map = {
        "btc": "bitcoin",
        "eth": "ethereum",
        "sol": "solana",
        "bnb": "binancecoin",
        "matic": "matic-network",
        "arb": "arbitrum",
        "op": "optimism",
        "avax": "avalanche-2",
        "base": "base",
        "link": "chainlink",
        "uni": "uniswap",
        "aave": "aave",
        "pepe": "pepe",
        "wif": "dogwifcoin",
        "bonk": "bonk",
    }
    coin_id = symbol_map.get(symbol, symbol)
    
    try:
        resp = requests.get(
            f"{COINGECKO_API}/simple/price",
            params={"ids": coin_id, "vs_currencies": "usd"},
            timeout=10
        )
        data = resp.json()
        if coin_id in data:
            return data[coin_id]["usd"]
    except Exception as e:
        print(f"⚠️ Price fetch error: {e}")
    return None

def init_portfolio():
    """Initialize portfolio"""
    config = load_json(CONFIG_FILE, DEFAULT_CONFIG)
    save_json(CONFIG_FILE, config)
    
    portfolio = {
        "balance_usd": config["initial_balance"],
        "holdings": {},  # {symbol: {amount, avg_price, total_cost}}
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }
    save_json(PORTFOLIO_FILE, portfolio)
    save_json(TRADES_FILE, [])
    
    print(f"✅ Portfolio initialized: ${config['initial_balance']:,.2f}")
    return portfolio

def get_portfolio():
    """Get current portfolio"""
    if not PORTFOLIO_FILE.exists():
        return init_portfolio()
    return load_json(PORTFOLIO_FILE, {})

def buy(symbol, amount_usd):
    """Buy token with USD amount"""
    symbol = symbol.upper()
    price = get_price(symbol)
    if not price:
        print(f"❌ Cannot get price for {symbol}")
        return False
    
    portfolio = get_portfolio()
    config = load_json(CONFIG_FILE, DEFAULT_CONFIG)
    
    # Check balance
    if amount_usd > portfolio["balance_usd"]:
        print(f"❌ Insufficient balance. Have: ${portfolio['balance_usd']:,.2f}, Need: ${amount_usd:,.2f}")
        return False
    
    # Calculate with fees & slippage
    fee = amount_usd * (config["fee_percent"] / 100)
    slippage = amount_usd * (config["slippage_percent"] / 100)
    effective_amount = amount_usd - fee - slippage
    tokens_bought = effective_amount / price
    
    # Update portfolio
    portfolio["balance_usd"] -= amount_usd
    
    if symbol not in portfolio["holdings"]:
        portfolio["holdings"][symbol] = {"amount": 0, "avg_price": 0, "total_cost": 0}
    
    holding = portfolio["holdings"][symbol]
    new_total_cost = holding["total_cost"] + effective_amount
    new_amount = holding["amount"] + tokens_bought
    holding["avg_price"] = new_total_cost / new_amount if new_amount > 0 else 0
    holding["amount"] = new_amount
    holding["total_cost"] = new_total_cost
    
    portfolio["updated_at"] = datetime.now().isoformat()
    save_json(PORTFOLIO_FILE, portfolio)
    
    # Log trade
    trades = load_json(TRADES_FILE, [])
    trades.append({
        "type": "BUY",
        "symbol": symbol,
        "amount_usd": amount_usd,
        "price": price,
        "tokens": tokens_bought,
        "fee": fee,
        "slippage": slippage,
        "timestamp": datetime.now().isoformat(),
    })
    save_json(TRADES_FILE, trades)
    
    print(f"✅ BUY {symbol}")
    print(f"   Amount: ${amount_usd:,.2f}")
    print(f"   Price: ${price:,.6f}")
    print(f"   Tokens: {tokens_bought:,.6f} {symbol}")
    print(f"   Fee: ${fee:,.2f} | Slippage: ${slippage:,.2f}")
    print(f"   Balance: ${portfolio['balance_usd']:,.2f}")
    return True

def sell(symbol, percent=100):
    """Sell token (percent of holdings)"""
    symbol = symbol.upper()
    price = get_price(symbol)
    if not price:
        print(f"❌ Cannot get price for {symbol}")
        return False
    
    portfolio = get_portfolio()
    config = load_json(CONFIG_FILE, DEFAULT_CONFIG)
    
    if symbol not in portfolio["holdings"] or portfolio["holdings"][symbol]["amount"] <= 0:
        print(f"❌ No {symbol} holdings")
        return False
    
    holding = portfolio["holdings"][symbol]
    tokens_to_sell = holding["amount"] * (percent / 100)
    gross_value = tokens_to_sell * price
    
    # Calculate with fees & slippage
    fee = gross_value * (config["fee_percent"] / 100)
    slippage = gross_value * (config["slippage_percent"] / 100)
    net_value = gross_value - fee - slippage
    
    # Calculate P&L
    cost_basis = holding["avg_price"] * tokens_to_sell
    pnl = net_value - cost_basis
    pnl_percent = (pnl / cost_basis * 100) if cost_basis > 0 else 0
    
    # Update portfolio
    portfolio["balance_usd"] += net_value
    holding["amount"] -= tokens_to_sell
    holding["total_cost"] -= cost_basis
    
    if holding["amount"] <= 0.000001:
        del portfolio["holdings"][symbol]
    
    portfolio["updated_at"] = datetime.now().isoformat()
    save_json(PORTFOLIO_FILE, portfolio)
    
    # Log trade
    trades = load_json(TRADES_FILE, [])
    trades.append({
        "type": "SELL",
        "symbol": symbol,
        "tokens": tokens_to_sell,
        "price": price,
        "gross_value": gross_value,
        "net_value": net_value,
        "fee": fee,
        "slippage": slippage,
        "pnl": pnl,
        "pnl_percent": pnl_percent,
        "timestamp": datetime.now().isoformat(),
    })
    save_json(TRADES_FILE, trades)
    
    pnl_emoji = "🟢" if pnl >= 0 else "🔴"
    print(f"✅ SELL {symbol} ({percent}%)")
    print(f"   Tokens: {tokens_to_sell:,.6f} {symbol}")
    print(f"   Price: ${price:,.6f}")
    print(f"   Gross: ${gross_value:,.2f} | Net: ${net_value:,.2f}")
    print(f"   {pnl_emoji} P&L: ${pnl:,.2f} ({pnl_percent:+.2f}%)")
    print(f"   Balance: ${portfolio['balance_usd']:,.2f}")
    return True

def status():
    """Show portfolio status"""
    portfolio = get_portfolio()
    config = load_json(CONFIG_FILE, DEFAULT_CONFIG)
    trades = load_json(TRADES_FILE, [])
    
    print("\n" + "="*50)
    print("📊 PAPER TRADE PORTFOLIO")
    print("="*50)
    
    total_value = portfolio["balance_usd"]
    
    print(f"\n💵 Cash: ${portfolio['balance_usd']:,.2f}")
    
    if portfolio["holdings"]:
        print(f"\n📈 Holdings:")
        for symbol, holding in portfolio["holdings"].items():
            price = get_price(symbol) or 0
            current_value = holding["amount"] * price
            pnl = current_value - holding["total_cost"]
            pnl_percent = (pnl / holding["total_cost"] * 100) if holding["total_cost"] > 0 else 0
            pnl_emoji = "🟢" if pnl >= 0 else "🔴"
            
            total_value += current_value
            
            print(f"   {symbol}:")
            print(f"      Amount: {holding['amount']:,.6f}")
            print(f"      Avg Price: ${holding['avg_price']:,.6f}")
            print(f"      Current: ${price:,.6f}")
            print(f"      Value: ${current_value:,.2f}")
            print(f"      {pnl_emoji} P&L: ${pnl:,.2f} ({pnl_percent:+.2f}%)")
    
    # Total P&L
    initial = config["initial_balance"]
    total_pnl = total_value - initial
    total_pnl_percent = (total_pnl / initial * 100) if initial > 0 else 0
    pnl_emoji = "🟢" if total_pnl >= 0 else "🔴"
    
    print(f"\n{'='*50}")
    print(f"💰 Total Value: ${total_value:,.2f}")
    print(f"{pnl_emoji} Total P&L: ${total_pnl:,.2f} ({total_pnl_percent:+.2f}%)")
    
    # Trade stats
    if trades:
        wins = sum(1 for t in trades if t.get("type") == "SELL" and t.get("pnl", 0) > 0)
        losses = sum(1 for t in trades if t.get("type") == "SELL" and t.get("pnl", 0) < 0)
        total_trades = wins + losses
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
        
        print(f"\n📊 Stats:")
        print(f"   Total Trades: {len(trades)}")
        print(f"   Wins: {wins} | Losses: {losses}")
        print(f"   Win Rate: {win_rate:.1f}%")
    
    print("="*50 + "\n")
    return total_value

def history(limit=10):
    """Show trade history"""
    trades = load_json(TRADES_FILE, [])
    
    print("\n📜 TRADE HISTORY (last {})".format(limit))
    print("-"*60)
    
    for trade in trades[-limit:]:
        ts = trade["timestamp"][:16].replace("T", " ")
        if trade["type"] == "BUY":
            print(f"[{ts}] 🟢 BUY {trade['symbol']} | ${trade['amount_usd']:,.2f} @ ${trade['price']:,.6f}")
        else:
            pnl_emoji = "🟢" if trade.get("pnl", 0) >= 0 else "🔴"
            print(f"[{ts}] 🔴 SELL {trade['symbol']} | ${trade['net_value']:,.2f} | {pnl_emoji} P&L: ${trade.get('pnl', 0):,.2f}")
    
    print("-"*60)

def reset():
    """Reset portfolio"""
    init_portfolio()
    print("✅ Portfolio reset")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python paper_trade.py status")
        print("  python paper_trade.py buy <symbol> <amount_usd>")
        print("  python paper_trade.py sell <symbol> [percent]")
        print("  python paper_trade.py history [limit]")
        print("  python paper_trade.py reset")
        sys.exit(0)
    
    cmd = sys.argv[1].lower()
    
    if cmd == "status":
        status()
    elif cmd == "buy" and len(sys.argv) >= 4:
        buy(sys.argv[2], float(sys.argv[3]))
    elif cmd == "sell" and len(sys.argv) >= 3:
        percent = float(sys.argv[3]) if len(sys.argv) >= 4 else 100
        sell(sys.argv[2], percent)
    elif cmd == "history":
        limit = int(sys.argv[2]) if len(sys.argv) >= 3 else 10
        history(limit)
    elif cmd == "reset":
        reset()
    else:
        print("❌ Invalid command")
