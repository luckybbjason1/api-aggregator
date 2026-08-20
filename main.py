"""
API Aggregator Service - 自动赚钱服务
聚合多个数据源 API，提供统一接口
"""

from fastapi import FastAPI, HTTPException
import httpx
import asyncio
from typing import Dict, List, Optional
import json

app = FastAPI(title="API Aggregator Service", version="1.0.0")

# 配置 API 密钥 (实际部署时从环境变量读取)
API_KEYS = {
    "crypto": ["BINANCE_KEY", "COINBASE_KEY", "KRAKEN_KEY"],
    "weather": ["OPENWEATHER_KEY", "WEATHERAPI_KEY"],
    "news": ["NEWSAPI_KEY", "MEDIASTACK_KEY"],
    "github": ["GITHUB_TOKEN"],
}

@app.get("/")
async def root():
    return {
        "message": "API Aggregator Service",
        "version": "1.0.0",
        "endpoints": [
            "/api/v1/crypto/{symbol}",
            "/api/v1/weather/{city}",
            "/api/v1/news/{query}",
            "/api/v1/github/repos/{owner}/{repo}"
        ]
    }

@app.get("/api/v1/crypto/{symbol}")
async def get_crypto_price(symbol: str):
    """获取加密货币价格"""
    symbol = symbol.upper()
    
    # 尝试多个数据源
    sources = []
    
    # Binance
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT")
            if resp.status_code == 200:
                data = resp.json()
                sources.append({"source": "Binance", "price": float(data['price'])})
    except:
        pass
    
    # Coinbase
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"https://api.coinbase.com/v2/prices/{symbol}-USD/spot")
            if resp.status_code == 200:
                data = resp.json()
                sources.append({"source": "Coinbase", "price": float(data['data']['amount'])})
    except:
        pass
    
    if not sources:
        raise HTTPException(status_code=404, detail="Price not found")
    
    # 返回平均价格
    avg_price = sum(s['price'] for s in sources) / len(sources)
    
    return {
        "symbol": symbol,
        "price_usd": avg_price,
        "sources": len(sources),
        "timestamp": asyncio.get_event_loop().time()
    }

@app.get("/api/v1/weather/{city}")
async def get_weather(city: str):
    """获取天气数据"""
    # 模拟天气数据 (实际部署时调用真实 API)
    return {
        "city": city,
        "temperature": 22,
        "humidity": 65,
        "condition": "晴朗",
        "sources": 2
    }

@app.get("/api/v1/news/{query}")
async def get_news(query: str):
    """获取新闻"""
    return {
        "query": query,
        "articles": [],
        "sources": 2
    }

@app.get("/api/v1/github/repos/{owner}/{repo}")
async def get_github_repo(owner: str, repo: str):
    """获取 GitHub 仓库信息"""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"https://api.github.com/repos/{owner}/{repo}")
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "name": data['full_name'],
                    "stars": data['stargazers_count'],
                    "forks": data['forks_count'],
                    "description": data.get('description', ''),
                    "language": data.get('language', '')
                }
            else:
                raise HTTPException(status_code=404, detail="Repository not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy"}
