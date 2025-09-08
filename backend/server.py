from fastapi import FastAPI, APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import json
import asyncio
import random
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Configuration
CHAIN_MODE = os.environ.get('CHAIN_MODE', 'mock')  # 'mock' or 'live'
NODE_RPC_URL = os.environ.get('NODE_RPC_URL', '')

# Create the main app
app = FastAPI(title="Regam Blockchain API", version="1.0.0")
api_router = APIRouter(prefix="/api")

# Models
class Block(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    hash: str
    height: int
    parent_hash: str
    timestamp: datetime
    tx_count: int
    producer: str
    gas_used: int
    tps_window: float
    energy_kwh_window: float
    size_bytes: int

class Transaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    hash: str
    block_height: int
    timestamp: datetime
    from_address: str
    to_address: str
    value: float
    fee: float
    status: str
    method: str
    gas_used: int

class Validator(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    address: str
    voting_power: int
    commission: float
    uptime_30d: float
    total_staked: float
    self_stake: float
    status: str

class Metrics(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime
    tps: float
    latency_ms: float
    energy_kwh: float
    nodes_online: int
    total_transactions: int
    total_blocks: int

class Address(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    address: str
    balance: float
    nonce: int
    tags: List[str] = []
    transaction_count: int

class WalletTransaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    address: str
    direction: str  # 'sent' or 'received'
    amount: float
    tx_hash: str
    status: str
    timestamp: datetime

class SendTransactionRequest(BaseModel):
    from_address: str
    to_address: str
    amount: float
    fee_estimate: Optional[float] = None

class FeeEstimateRequest(BaseModel):
    from_address: str
    to_address: str
    amount: float

class StakeRequest(BaseModel):
    validator_address: str
    amount: float
    delegator_address: str

# Mock Data Generators
def generate_address():
    return f"regam1{''.join(random.choices('0123456789abcdef', k=38))}"

def generate_hash():
    return '0x' + ''.join(random.choices('0123456789abcdef', k=64))

async def generate_mock_block(height: int) -> Dict:
    return {
        "hash": generate_hash(),
        "height": height,
        "parent_hash": generate_hash(),
        "timestamp": datetime.now(timezone.utc) - timedelta(seconds=random.randint(0, 3600)),
        "tx_count": random.randint(50, 500),
        "producer": generate_address(),
        "gas_used": random.randint(1000000, 5000000),
        "tps_window": random.uniform(1800000, 2100000),  # Around 2M TPS
        "energy_kwh_window": random.uniform(0.001, 0.005),  # Very eco-friendly
        "size_bytes": random.randint(50000, 200000)
    }

async def generate_mock_transaction(block_height: int) -> Dict:
    return {
        "hash": generate_hash(),
        "block_height": block_height,
        "timestamp": datetime.now(timezone.utc) - timedelta(seconds=random.randint(0, 3600)),
        "from_address": generate_address(),
        "to_address": generate_address(),
        "value": random.uniform(0.1, 1000),
        "fee": random.uniform(0.0001, 0.001),  # Very low fees
        "status": random.choice(["confirmed", "confirmed", "confirmed", "pending"]),
        "method": random.choice(["transfer", "stake", "unstake", "vote", "contract_call"]),
        "gas_used": random.randint(21000, 100000)
    }

async def generate_mock_validator() -> Dict:
    return {
        "address": generate_address(),
        "voting_power": random.randint(1000000, 10000000),
        "commission": random.uniform(0.01, 0.1),
        "uptime_30d": random.uniform(0.95, 1.0),
        "total_staked": random.uniform(100000, 1000000),
        "self_stake": random.uniform(10000, 100000),
        "status": random.choice(["active", "active", "active", "inactive"])
    }

async def generate_mock_metrics() -> Dict:
    return {
        "timestamp": datetime.now(timezone.utc),
        "tps": random.uniform(1800000, 2100000),  # Around 2M TPS
        "latency_ms": random.uniform(0.1, 2.0),  # Very fast
        "energy_kwh": random.uniform(0.001, 0.005),  # Eco-friendly
        "nodes_online": random.randint(1000, 5000),
        "total_transactions": random.randint(10000000, 50000000),
        "total_blocks": random.randint(100000, 500000)
    }

# API Endpoints

# Explorer Endpoints
@api_router.get("/blocks")
async def get_blocks(limit: int = Query(20, le=100), cursor: Optional[str] = None):
    if CHAIN_MODE == 'mock':
        blocks = []
        start_height = int(cursor) if cursor else 1000000
        for i in range(limit):
            block_data = await generate_mock_block(start_height - i)
            blocks.append(Block(**block_data))
        
        next_cursor = str(start_height - limit) if start_height - limit > 0 else None
        return {
            "blocks": blocks,
            "next_cursor": next_cursor,
            "has_more": next_cursor is not None
        }
    else:
        # Live mode - would connect to actual blockchain node
        raise HTTPException(status_code=501, detail="Live mode not implemented yet")

@api_router.get("/blocks/{block_id}")
async def get_block(block_id: str):
    if CHAIN_MODE == 'mock':
        # Try to parse as height first, then as hash
        try:
            height = int(block_id)
            block_data = await generate_mock_block(height)
        except ValueError:
            # Treat as hash
            block_data = await generate_mock_block(random.randint(1, 1000000))
            block_data["hash"] = block_id
        
        # Generate transactions for this block
        transactions = []
        tx_count = random.randint(50, 200)
        for _ in range(tx_count):
            tx_data = await generate_mock_transaction(block_data["height"])
            transactions.append(Transaction(**tx_data))
        
        return {
            "block": Block(**block_data),
            "transactions": transactions
        }
    else:
        raise HTTPException(status_code=501, detail="Live mode not implemented yet")

@api_router.get("/tx/{tx_hash}")
async def get_transaction(tx_hash: str):
    if CHAIN_MODE == 'mock':
        tx_data = await generate_mock_transaction(random.randint(1, 1000000))
        tx_data["hash"] = tx_hash
        return Transaction(**tx_data)
    else:
        raise HTTPException(status_code=501, detail="Live mode not implemented yet")

@api_router.get("/address/{address}")
async def get_address(address: str):
    if CHAIN_MODE == 'mock':
        # Generate address info
        address_data = {
            "address": address,
            "balance": random.uniform(10, 10000),
            "nonce": random.randint(0, 1000),
            "tags": random.choice([[], ["exchange"], ["validator"], ["dapp"]]),
            "transaction_count": random.randint(10, 10000)
        }
        
        # Generate recent transactions
        transactions = []
        for _ in range(10):
            tx_data = await generate_mock_transaction(random.randint(1, 1000000))
            # Make some transactions involve this address
            if random.choice([True, False]):
                tx_data["from_address"] = address
            else:
                tx_data["to_address"] = address
            transactions.append(Transaction(**tx_data))
        
        return {
            "address": Address(**address_data),
            "recent_transactions": transactions
        }
    else:
        raise HTTPException(status_code=501, detail="Live mode not implemented yet")

@api_router.get("/validators")
async def get_validators():
    if CHAIN_MODE == 'mock':
        validators = []
        for _ in range(50):
            validator_data = await generate_mock_validator()
            validators.append(Validator(**validator_data))
        return {"validators": validators}
    else:
        raise HTTPException(status_code=501, detail="Live mode not implemented yet")

@api_router.get("/metrics/tps")
async def get_tps_metrics(window: str = Query("5m")):
    if CHAIN_MODE == 'mock':
        # Generate time series data
        data_points = []
        now = datetime.now(timezone.utc)
        
        # Generate 20 data points for the window
        for i in range(20):
            timestamp = now - timedelta(minutes=i)
            tps = random.uniform(1800000, 2100000)  # Around 2M TPS
            data_points.append({
                "timestamp": timestamp,
                "tps": tps
            })
        
        return {
            "window": window,
            "data": list(reversed(data_points)),
            "average_tps": sum(d["tps"] for d in data_points) / len(data_points)
        }
    else:
        raise HTTPException(status_code=501, detail="Live mode not implemented yet")

@api_router.get("/metrics/energy")
async def get_energy_metrics(window: str = Query("1h")):
    if CHAIN_MODE == 'mock':
        data_points = []
        now = datetime.now(timezone.utc)
        
        for i in range(20):
            timestamp = now - timedelta(hours=i)
            energy = random.uniform(0.001, 0.005)  # Very eco-friendly
            data_points.append({
                "timestamp": timestamp,
                "energy_kwh": energy
            })
        
        return {
            "window": window,
            "data": list(reversed(data_points)),
            "average_energy": sum(d["energy_kwh"] for d in data_points) / len(data_points)
        }
    else:
        raise HTTPException(status_code=501, detail="Live mode not implemented yet")

@api_router.get("/search")
async def search(q: str = Query(..., min_length=1)):
    if CHAIN_MODE == 'mock':
        results = []
        
        # Try to determine what type of search this is
        if q.isdigit():
            # Block height
            block_data = await generate_mock_block(int(q))
            results.append({
                "type": "block",
                "data": Block(**block_data)
            })
        elif q.startswith("0x") and len(q) == 66:
            # Transaction hash
            tx_data = await generate_mock_transaction(random.randint(1, 1000000))
            tx_data["hash"] = q
            results.append({
                "type": "transaction",
                "data": Transaction(**tx_data)
            })
        elif q.startswith("regam1"):
            # Address
            address_data = {
                "address": q,
                "balance": random.uniform(10, 10000),
                "nonce": random.randint(0, 1000),
                "tags": [],
                "transaction_count": random.randint(10, 1000)
            }
            results.append({
                "type": "address",
                "data": Address(**address_data)
            })
        
        return {"query": q, "results": results}
    else:
        raise HTTPException(status_code=501, detail="Live mode not implemented yet")

# Wallet Endpoints
@api_router.get("/wallet/{address}/balance")
async def get_wallet_balance(address: str):
    if CHAIN_MODE == 'mock':
        return {
            "address": address,
            "balance": random.uniform(10, 10000),
            "staked_balance": random.uniform(0, 1000),
            "pending_rewards": random.uniform(0, 10)
        }
    else:
        raise HTTPException(status_code=501, detail="Live mode not implemented yet")

@api_router.get("/wallet/{address}/transactions")
async def get_wallet_transactions(address: str, limit: int = Query(50, le=100)):
    if CHAIN_MODE == 'mock':
        transactions = []
        for _ in range(limit):
            tx_data = await generate_mock_transaction(random.randint(1, 1000000))
            # Make transaction involve this address
            if random.choice([True, False]):
                tx_data["from_address"] = address
                direction = "sent"
            else:
                tx_data["to_address"] = address
                direction = "received"
            
            wallet_tx = {
                "user_id": "mock_user",
                "address": address,
                "direction": direction,
                "amount": tx_data["value"],
                "tx_hash": tx_data["hash"],
                "status": tx_data["status"],
                "timestamp": tx_data["timestamp"]
            }
            transactions.append(WalletTransaction(**wallet_tx))
        
        return {"transactions": transactions}
    else:
        raise HTTPException(status_code=501, detail="Live mode not implemented yet")

@api_router.post("/wallet/send")
async def send_transaction(request: SendTransactionRequest):
    if CHAIN_MODE == 'mock':
        # Simulate transaction creation
        tx_hash = generate_hash()
        return {
            "tx_hash": tx_hash,
            "status": "pending",
            "estimated_confirmation": "2-3 seconds",
            "fee": request.fee_estimate or random.uniform(0.0001, 0.001)
        }
    else:
        raise HTTPException(status_code=501, detail="Live mode not implemented yet")

@api_router.post("/wallet/estimateFee")
async def estimate_fee(request: FeeEstimateRequest):
    if CHAIN_MODE == 'mock':
        # Very low fees for Regam blockchain
        base_fee = 0.0001
        amount_fee = request.amount * 0.00001  # 0.001% of amount
        total_fee = base_fee + amount_fee
        
        return {
            "base_fee": base_fee,
            "amount_fee": amount_fee,
            "total_fee": total_fee,
            "estimated_confirmation": "2-3 seconds"
        }
    else:
        raise HTTPException(status_code=501, detail="Live mode not implemented yet")

@api_router.post("/wallet/stake")
async def stake_tokens(request: StakeRequest):
    if CHAIN_MODE == 'mock':
        return {
            "status": "success",
            "tx_hash": generate_hash(),
            "validator": request.validator_address,
            "staked_amount": request.amount,
            "estimated_rewards_apy": random.uniform(0.08, 0.15),  # 8-15% APY
            "estimated_confirmation": "2-3 seconds"
        }
    else:
        raise HTTPException(status_code=501, detail="Live mode not implemented yet")

@api_router.get("/wallet/multi")
async def get_multi_wallet_info(addresses: str = Query(...)):
    if CHAIN_MODE == 'mock':
        address_list = addresses.split(',')
        wallets = []
        
        for addr in address_list:
            wallet_info = {
                "address": addr.strip(),
                "balance": random.uniform(10, 10000),
                "staked_balance": random.uniform(0, 1000),
                "nickname": f"Wallet {addr[-4:]}"
            }
            wallets.append(wallet_info)
        
        return {"wallets": wallets}
    else:
        raise HTTPException(status_code=501, detail="Live mode not implemented yet")

# Real-time streaming endpoint
@api_router.get("/stream/metrics")
async def stream_metrics():
    async def generate_metrics_stream():
        while True:
            metrics_data = await generate_mock_metrics()
            metrics = Metrics(**metrics_data)
            yield f"data: {metrics.json()}\n\n"
            await asyncio.sleep(2)  # Update every 2 seconds
    
    return StreamingResponse(
        generate_metrics_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }
    )

# System info
@api_router.get("/system/info")
async def get_system_info():
    return {
        "blockchain_name": "Regam Blockchain",
        "version": "1.0.0",
        "mode": CHAIN_MODE,
        "features": {
            "max_tps": "2,000,000",
            "avg_confirmation_time": "2-3 seconds",
            "energy_per_transaction": "0.001-0.005 kWh",
            "consensus": "Proof of Stake + Energy Efficiency",
            "avg_fee": "0.0001-0.001 RGC"
        },
        "network_stats": {
            "total_validators": random.randint(1000, 5000),
            "online_nodes": random.randint(3000, 8000),
            "total_staked": f"{random.randint(10000000, 50000000):,} RGC"
        }
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()