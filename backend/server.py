from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import bcrypt
import jwt
from enum import Enum

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

# Create the main app
app = FastAPI(title="Amicale Anouar API", version="1.0.0")
api_router = APIRouter(prefix="/api")
security = HTTPBearer()

# Enums
class Sex(str, Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"

class MemberStatus(str, Enum):
    PENDING = "Pending"
    ACTIVE = "Active"
    INACTIVE = "Inactive"

class PaymentMethod(str, Enum):
    CASH = "Cash"
    BANK = "Bank"
    MOBILE = "Mobile"

class UserRole(str, Enum):
    ADMIN = "Admin"
    STAFF = "Staff"
    ADHERENT = "Adherent"

# Models
class ProjectType(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    default_due: float
    active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ProjectTypeCreate(BaseModel):
    name: str
    default_due: float

class ProjectTypeUpdate(BaseModel):
    name: Optional[str] = None
    default_due: Optional[float] = None
    active: Optional[bool] = None

class Member(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    full_name: str
    sex: Sex
    phone: str
    job: Optional[str] = None
    project_type: str
    project_type_id: str
    total_due: float = 0.0
    amount_paid: float = 0.0
    balance: float = 0.0
    points: int = 0
    status: MemberStatus = MemberStatus.PENDING
    join_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    notes: Optional[str] = None

class MemberCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    sex: Sex
    phone: str = Field(..., min_length=8, max_length=15)
    job: Optional[str] = None
    project_type_id: str
    initial_paid: float = 0.0

class MemberUpdate(BaseModel):
    full_name: Optional[str] = None
    sex: Optional[Sex] = None
    phone: Optional[str] = None
    job: Optional[str] = None
    project_type_id: Optional[str] = None
    total_due: Optional[float] = None
    status: Optional[MemberStatus] = None
    notes: Optional[str] = None
    points: Optional[int] = None

class Payment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    member_id: str
    amount: float
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    method: PaymentMethod
    note: Optional[str] = None
    recorded_by: str
    recorded_by_name: str

class PaymentCreate(BaseModel):
    amount: float = Field(..., gt=0)
    method: PaymentMethod
    note: Optional[str] = None

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: EmailStr
    role: UserRole = UserRole.STAFF
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.STAFF

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class PointTransaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    member_id: str
    points: int
    transaction_type: str  # "payment", "manual", "bonus", "deduction"
    description: str
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    recorded_by: str
    recorded_by_name: str
    related_payment_id: Optional[str] = None

class PointTransactionCreate(BaseModel):
    points: int
    transaction_type: str = "manual"
    description: str

class ReportsSummary(BaseModel):
    total_members: int
    total_collected: float
    total_outstanding: float
    active_members: int
    pending_members: int
    total_points_distributed: int
    average_points_per_member: float

# Rewards System Models
class RewardCategory(str, Enum):
    MATERIEL = "Materiel"
    SERVICES = "Services"
    REDUCTIONS = "Reductions"
    PRIVILEGES = "Privileges"

class RedemptionStatus(str, Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    DELIVERED = "Delivered"
    REJECTED = "Rejected"
    CANCELED = "Canceled"

class Reward(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    category: RewardCategory
    description: Optional[str] = None
    cost_points: int = Field(..., ge=0)
    stock: int = Field(..., ge=0)
    is_active: bool = True
    image_url: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class RewardCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    category: RewardCategory
    description: Optional[str] = None
    cost_points: int = Field(..., ge=0)
    stock: int = Field(..., ge=0)
    image_url: Optional[str] = None

class RewardUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[RewardCategory] = None
    description: Optional[str] = None
    cost_points: Optional[int] = None
    stock: Optional[int] = None
    is_active: Optional[bool] = None
    image_url: Optional[str] = None

class RewardRedemption(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    member_id: str
    member_name: str
    reward_id: str
    reward_name: str
    points_cost: int
    status: RedemptionStatus = RedemptionStatus.PENDING
    note: Optional[str] = None
    created_by: Optional[str] = None
    approved_by: Optional[str] = None
    approved_by_name: Optional[str] = None
    delivered_by: Optional[str] = None
    delivered_by_name: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class RedemptionCreate(BaseModel):
    reward_id: str
    note: Optional[str] = None

class RedemptionStatusUpdate(BaseModel):
    note: Optional[str] = None

# Levels & Badges System Models
class Level(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    min_points: int = Field(..., ge=0)
    benefits: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class LevelCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    min_points: int = Field(..., ge=0)
    benefits: Optional[str] = None

class Badge(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    code: str = Field(..., pattern=r'^[A-Z0-9_]+$')  # e.g., "REGULAR_PAYER", "TOP_3_MONTH"
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class BadgeCreate(BaseModel):
    code: str = Field(..., pattern=r'^[A-Z_]+$')
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    image_url: Optional[str] = None

class MemberBadge(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    member_id: str
    badge_id: str
    badge_code: str
    badge_name: str
    awarded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class MemberLevel(BaseModel):
    current_level: Level
    next_level: Optional[Level] = None
    progress_percentage: float = 0.0
    points_to_next: int = 0

class LeaderboardEntry(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    period: str  # "monthly:2025-09" or "all_time"
    rank: int
    member_id: str
    member_name: str
    points: int
    level_name: Optional[str] = None
    badge_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class LeaderboardResponse(BaseModel):
    period: str
    entries: List[LeaderboardEntry]
    total_entries: int
    generated_at: datetime

# Helper Functions
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = await db.users.find_one({"id": user_id})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        user = clean_mongo_doc(user)
        return User(**user)
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def require_admin_or_staff(current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.ADMIN, UserRole.STAFF]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return current_user

async def calculate_balance(member_id: str) -> dict:
    """Calculate member's total paid and balance"""
    payments = await db.payments.find({"member_id": member_id}).to_list(None)
    total_paid = sum(payment["amount"] for payment in payments)
    
    member = await db.members.find_one({"id": member_id})
    if not member:
        return {"amount_paid": 0.0, "balance": 0.0}
    
    balance = member["total_due"] - total_paid
    return {"amount_paid": total_paid, "balance": balance}

def clean_mongo_doc(doc):
    """Remove MongoDB ObjectId from document"""
    if doc and "_id" in doc:
        del doc["_id"]
    return doc

def calculate_points_from_payment(amount: float) -> int:
    """Calculate points based on payment amount (1 point per 10 MAD)"""
    return int(amount // 10)

async def add_points_transaction(member_id: str, points: int, transaction_type: str, description: str, recorded_by: str, recorded_by_name: str, related_payment_id: str = None):
    """Add a points transaction and update member points"""
    transaction = PointTransaction(
        member_id=member_id,
        points=points,
        transaction_type=transaction_type,
        description=description,
        recorded_by=recorded_by,
        recorded_by_name=recorded_by_name,
        related_payment_id=related_payment_id
    )
    
    await db.point_transactions.insert_one(transaction.dict())
    
    # Update member points
    member = await db.members.find_one({"id": member_id})
    if member:
        new_points = member.get("points", 0) + points
        await db.members.update_one(
            {"id": member_id},
            {"$set": {"points": max(0, new_points)}}  # Ensure points don't go negative
        )

async def get_member_points_balance(member_id: str) -> int:
    """Get current points balance for a member"""
    member = await db.members.find_one({"id": member_id})
    return member.get("points", 0) if member else 0

async def can_member_redeem(member_id: str, points_cost: int) -> bool:
    """Check if member has enough points to redeem"""
    balance = await get_member_points_balance(member_id)
    return balance >= points_cost

async def count_pending_redemptions(member_id: str) -> int:
    """Count pending redemptions for a member (anti-abuse)"""
    count = await db.reward_redemptions.count_documents({
        "member_id": member_id,
        "status": RedemptionStatus.PENDING
    })
    return count

# Levels & Badges Helper Functions
async def calculate_total_points_earned(member_id: str) -> int:
    """Calculate total points earned (excluding redemptions)"""
    pipeline = [
        {
            "$match": {
                "member_id": member_id,
                "transaction_type": {"$in": ["payment", "bonus", "manual"]},
                "points": {"$gt": 0}
            }
        },
        {
            "$group": {
                "_id": None,
                "total": {"$sum": "$points"}
            }
        }
    ]
    
    result = await db.point_transactions.aggregate(pipeline).to_list(None)
    return result[0]["total"] if result else 0

async def get_member_level(member_id: str) -> MemberLevel:
    """Get member's current level and progression"""
    total_earned = await calculate_total_points_earned(member_id)
    
    # Get all levels sorted by min_points
    levels = await db.levels.find().sort("min_points", 1).to_list(None)
    
    current_level = None
    next_level = None
    
    # Find current level
    for level in levels:
        if total_earned >= level["min_points"]:
            current_level = level
        elif current_level and not next_level:
            next_level = level
            break
    
    if not current_level and levels:
        current_level = levels[0]  # Default to first level
    
    # Calculate progress
    progress_percentage = 0.0
    points_to_next = 0
    
    if current_level and next_level:
        points_in_level = total_earned - current_level["min_points"]
        points_needed = next_level["min_points"] - current_level["min_points"]
        progress_percentage = (points_in_level / points_needed) * 100
        points_to_next = next_level["min_points"] - total_earned
    elif current_level and not next_level:
        progress_percentage = 100.0  # Max level reached
    
    return MemberLevel(
        current_level=Level(**current_level) if current_level else None,
        next_level=Level(**next_level) if next_level else None,
        progress_percentage=round(progress_percentage, 1),
        points_to_next=max(0, points_to_next)
    )

async def get_member_badges(member_id: str) -> List[MemberBadge]:
    """Get all badges for a member"""
    badges = await db.member_badges.find({"member_id": member_id}).sort("awarded_at", -1).to_list(None)
    for badge in badges:
        clean_mongo_doc(badge)
    return [MemberBadge(**badge) for badge in badges]

async def award_badge_to_member(member_id: str, badge_code: str, awarded_by: str = "system") -> bool:
    """Award a badge to a member (if not already awarded)"""
    # Check if badge exists
    badge = await db.badges.find_one({"code": badge_code})
    if not badge:
        return False
    
    # Check if already awarded
    existing = await db.member_badges.find_one({
        "member_id": member_id,
        "badge_id": badge["id"]
    })
    
    if existing:
        return False  # Already has this badge
    
    # Award the badge
    member_badge = MemberBadge(
        member_id=member_id,
        badge_id=badge["id"],
        badge_code=badge["code"],
        badge_name=badge["name"]
    )
    
    await db.member_badges.insert_one(member_badge.dict())
    return True

async def check_and_award_regular_payer_badge(member_id: str):
    """Check if member qualifies for regular payer badge (3 consecutive months with payments)"""
    # Get last 3 months of payments
    three_months_ago = datetime.now(timezone.utc) - timedelta(days=90)
    
    # Get payments grouped by month
    pipeline = [
        {
            "$match": {
                "member_id": member_id,
                "date": {"$gte": three_months_ago}
            }
        },
        {
            "$group": {
                "_id": {
                    "year": {"$year": "$date"},
                    "month": {"$month": "$date"}
                },
                "count": {"$sum": 1}
            }
        },
        {
            "$sort": {"_id.year": -1, "_id.month": -1}
        }
    ]
    
    monthly_payments = await db.payments.aggregate(pipeline).to_list(None)
    
    if len(monthly_payments) >= 3:
        # Check if last 3 months are consecutive
        months = [(result["_id"]["year"], result["_id"]["month"]) for result in monthly_payments[:3]]
        
        # Simple check for 3 consecutive months (can be improved)
        if len(months) == 3:
            await award_badge_to_member(member_id, "REGULAR_PAYER")

async def build_monthly_leaderboard(year: int, month: int):
    """Build leaderboard for a specific month"""
    # Calculate start and end dates for the month
    start_date = datetime(year, month, 1, tzinfo=timezone.utc)
    if month == 12:
        end_date = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
    else:
        end_date = datetime(year, month + 1, 1, tzinfo=timezone.utc)
    
    # Get points earned in this month (payment and bonus only)
    pipeline = [
        {
            "$match": {
                "date": {"$gte": start_date, "$lt": end_date},
                "transaction_type": {"$in": ["payment", "bonus"]},
                "points": {"$gt": 0}
            }
        },
        {
            "$group": {
                "_id": "$member_id",
                "total_points": {"$sum": "$points"}
            }
        },
        {
            "$sort": {"total_points": -1}
        }
    ]
    
    monthly_points = await db.point_transactions.aggregate(pipeline).to_list(None)
    
    period = f"monthly:{year}-{month:02d}"
    
    # Clear existing leaderboard for this period
    await db.leaderboards.delete_many({"period": period})
    
    # Create leaderboard entries
    rank = 1
    for entry in monthly_points:
        member = await db.members.find_one({"id": entry["_id"]})
        if member:
            member_level = await get_member_level(entry["_id"])
            member_badges = await get_member_badges(entry["_id"])
            
            leaderboard_entry = LeaderboardEntry(
                period=period,
                rank=rank,
                member_id=entry["_id"],
                member_name=member["full_name"],
                points=entry["total_points"],
                level_name=member_level.current_level.name if member_level.current_level else "Bronze",
                badge_count=len(member_badges)
            )
            
            await db.leaderboards.insert_one(leaderboard_entry.dict())
            
            # Award top 3 badge
            if rank <= 3:
                await award_badge_to_member(entry["_id"], "TOP_3_MONTH")
            
            rank += 1

async def build_all_time_leaderboard():
    """Build all-time leaderboard"""
    # Get all members and their total earned points
    members = await db.members.find().to_list(None)
    
    leaderboard_data = []
    for member in members:
        total_earned = await calculate_total_points_earned(member["id"])
        if total_earned > 0:
            member_level = await get_member_level(member["id"])
            member_badges = await get_member_badges(member["id"])
            
            leaderboard_data.append({
                "member_id": member["id"],
                "member_name": member["full_name"],
                "points": total_earned,
                "level_name": member_level.current_level.name if member_level.current_level else "Bronze",
                "badge_count": len(member_badges)
            })
    
    # Sort by points descending
    leaderboard_data.sort(key=lambda x: x["points"], reverse=True)
    
    period = "all_time"
    
    # Clear existing all-time leaderboard
    await db.leaderboards.delete_many({"period": period})
    
    # Create leaderboard entries
    for rank, data in enumerate(leaderboard_data, 1):
        leaderboard_entry = LeaderboardEntry(
            period=period,
            rank=rank,
            **data
        )
        
        await db.leaderboards.insert_one(leaderboard_entry.dict())

# Authentication Routes
@api_router.post("/auth/login", response_model=Token)
async def login(user_data: UserLogin):
    user = await db.users.find_one({"email": user_data.email})
    if not user or not verify_password(user_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user = clean_mongo_doc(user)
    access_token = create_access_token({"sub": user["id"]})
    user.pop("password_hash", None)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@api_router.post("/auth/register", response_model=Token)
async def register(user_data: UserCreate):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    hashed_password = hash_password(user_data.password)
    user = User(
        name=user_data.name,
        email=user_data.email,
        role=user_data.role
    )
    
    user_dict = user.dict()
    user_dict["password_hash"] = hashed_password
    
    await db.users.insert_one(user_dict)
    
    access_token = create_access_token({"sub": user.id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user.dict()
    }

# Public Member Registration
@api_router.post("/members/register", response_model=Member)
async def register_member(member_data: MemberCreate):
    # Check if phone already exists
    existing_member = await db.members.find_one({"phone": member_data.phone})
    if existing_member:
        raise HTTPException(status_code=400, detail="Phone number already registered")
    
    # Get project type
    project_type = await db.project_types.find_one({"id": member_data.project_type_id})
    if not project_type:
        raise HTTPException(status_code=404, detail="Project type not found")
    
    # Create member
    member = Member(
        full_name=member_data.full_name,
        sex=member_data.sex,
        phone=member_data.phone,
        job=member_data.job,
        project_type=project_type["name"],
        project_type_id=member_data.project_type_id,
        total_due=project_type["default_due"],
        amount_paid=member_data.initial_paid,
        balance=project_type["default_due"] - member_data.initial_paid
    )
    
    await db.members.insert_one(member.dict())
    
    # Create initial payment if amount was paid
    if member_data.initial_paid > 0:
        payment = Payment(
            member_id=member.id,
            amount=member_data.initial_paid,
            method=PaymentMethod.CASH,
            note="Initial payment during registration",
            recorded_by="system",
            recorded_by_name="System"
        )
        await db.payments.insert_one(payment.dict())
    
    return member

# Member Management Routes
@api_router.get("/members", response_model=List[Member])
async def get_members(
    query: Optional[str] = None,
    status: Optional[MemberStatus] = None,
    project_type_id: Optional[str] = None,
    current_user: User = Depends(require_admin_or_staff)
):
    filter_query = {}
    
    if query:
        filter_query["$or"] = [
            {"full_name": {"$regex": query, "$options": "i"}},
            {"phone": {"$regex": query, "$options": "i"}}
        ]
    
    if status:
        filter_query["status"] = status
        
    if project_type_id:
        filter_query["project_type_id"] = project_type_id
    
    members = await db.members.find(filter_query).to_list(None)
    
    # Update balances and clean docs
    for member in members:
        clean_mongo_doc(member)
        balance_info = await calculate_balance(member["id"])
        member.update(balance_info)
    
    return [Member(**member) for member in members]

@api_router.get("/members/{member_id}", response_model=Member)
async def get_member(
    member_id: str,
    current_user: User = Depends(require_admin_or_staff)
):
    member = await db.members.find_one({"id": member_id})
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    clean_mongo_doc(member)
    balance_info = await calculate_balance(member_id)
    member.update(balance_info)
    
    return Member(**member)

@api_router.put("/members/{member_id}", response_model=Member)
async def update_member(
    member_id: str,
    member_data: MemberUpdate,
    current_user: User = Depends(require_admin_or_staff)
):
    member = await db.members.find_one({"id": member_id})
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    update_data = {k: v for k, v in member_data.dict().items() if v is not None}
    
    if update_data:
        await db.members.update_one({"id": member_id}, {"$set": update_data})
    
    updated_member = await db.members.find_one({"id": member_id})
    clean_mongo_doc(updated_member)
    balance_info = await calculate_balance(member_id)
    updated_member.update(balance_info)
    
    return Member(**updated_member)

# Payment Routes
@api_router.post("/members/{member_id}/payments", response_model=Payment)
async def add_payment(
    member_id: str,
    payment_data: PaymentCreate,
    current_user: User = Depends(require_admin_or_staff)
):
    member = await db.members.find_one({"id": member_id})
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    payment = Payment(
        member_id=member_id,
        amount=payment_data.amount,
        method=payment_data.method,
        note=payment_data.note,
        recorded_by=current_user.id,
        recorded_by_name=current_user.name
    )
    
    await db.payments.insert_one(payment.dict())
    
    # Update member balance
    balance_info = await calculate_balance(member_id)
    await db.members.update_one(
        {"id": member_id},
        {"$set": balance_info}
    )
    
    # Calculate and add points for this payment
    points_earned = calculate_points_from_payment(payment_data.amount)
    if points_earned > 0:
        await add_points_transaction(
            member_id=member_id,
            points=points_earned,
            transaction_type="payment",
            description=f"Points gagnés pour paiement de {payment_data.amount} MAD",
            recorded_by=current_user.id,
            recorded_by_name=current_user.name,
            related_payment_id=payment.id
        )
    
    return payment

@api_router.get("/members/{member_id}/payments", response_model=List[Payment])
async def get_member_payments(
    member_id: str,
    current_user: User = Depends(require_admin_or_staff)
):
    payments = await db.payments.find({"member_id": member_id}).sort("date", -1).to_list(None)
    for payment in payments:
        clean_mongo_doc(payment)
    return [Payment(**payment) for payment in payments]

@api_router.get("/payments", response_model=List[Payment])
async def get_all_payments(
    current_user: User = Depends(require_admin_or_staff)
):
    payments = await db.payments.find().sort("date", -1).to_list(100)
    for payment in payments:
        clean_mongo_doc(payment)
    return [Payment(**payment) for payment in payments]

# Project Types Routes
@api_router.get("/project-types", response_model=List[ProjectType])
async def get_project_types():
    project_types = await db.project_types.find({"active": True}).to_list(None)
    for pt in project_types:
        clean_mongo_doc(pt)
    return [ProjectType(**pt) for pt in project_types]

@api_router.post("/project-types", response_model=ProjectType)
async def create_project_type(
    project_type_data: ProjectTypeCreate,
    current_user: User = Depends(require_admin_or_staff)
):
    # Check if name exists
    existing = await db.project_types.find_one({"name": project_type_data.name})
    if existing:
        raise HTTPException(status_code=400, detail="Project type name already exists")
    
    project_type = ProjectType(
        name=project_type_data.name,
        default_due=project_type_data.default_due
    )
    
    await db.project_types.insert_one(project_type.dict())
    return project_type

@api_router.put("/project-types/{project_type_id}", response_model=ProjectType)
async def update_project_type(
    project_type_id: str,
    project_type_data: ProjectTypeUpdate,
    current_user: User = Depends(require_admin_or_staff)
):
    update_data = {k: v for k, v in project_type_data.dict().items() if v is not None}
    
    if update_data:
        await db.project_types.update_one({"id": project_type_id}, {"$set": update_data})
    
    project_type = await db.project_types.find_one({"id": project_type_id})
    if not project_type:
        raise HTTPException(status_code=404, detail="Project type not found")
    
    clean_mongo_doc(project_type)
    return ProjectType(**project_type)

# Points Routes
@api_router.post("/members/{member_id}/points", response_model=PointTransaction)
async def add_points_to_member(
    member_id: str,
    points_data: PointTransactionCreate,
    current_user: User = Depends(require_admin_or_staff)
):
    member = await db.members.find_one({"id": member_id})
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    await add_points_transaction(
        member_id=member_id,
        points=points_data.points,
        transaction_type=points_data.transaction_type,
        description=points_data.description,
        recorded_by=current_user.id,
        recorded_by_name=current_user.name
    )
    
    # Return the transaction
    transaction = PointTransaction(
        member_id=member_id,
        points=points_data.points,
        transaction_type=points_data.transaction_type,
        description=points_data.description,
        recorded_by=current_user.id,
        recorded_by_name=current_user.name
    )
    
    return transaction

@api_router.get("/members/{member_id}/points", response_model=List[PointTransaction])
async def get_member_points_history(
    member_id: str,
    current_user: User = Depends(require_admin_or_staff)
):
    transactions = await db.point_transactions.find({"member_id": member_id}).sort("date", -1).to_list(None)
    for transaction in transactions:
        clean_mongo_doc(transaction)
    return [PointTransaction(**transaction) for transaction in transactions]

@api_router.get("/points/leaderboard")
async def get_points_leaderboard(
    limit: int = 10,
    current_user: User = Depends(require_admin_or_staff)
):
    """Get top members by points"""
    members = await db.members.find().sort("points", -1).limit(limit).to_list(None)
    for member in members:
        clean_mongo_doc(member)
    return [Member(**member) for member in members]

# Reports Routes
@api_router.get("/reports/summary", response_model=ReportsSummary)
async def get_reports_summary(
    current_user: User = Depends(require_admin_or_staff)
):
    # Get all members
    all_members = await db.members.find().to_list(None)
    
    # Calculate totals
    total_members = len(all_members)
    active_members = len([m for m in all_members if m["status"] == "Active"])
    pending_members = len([m for m in all_members if m["status"] == "Pending"])
    
    total_collected = 0.0
    total_outstanding = 0.0
    total_points = 0
    
    for member in all_members:
        clean_mongo_doc(member)
        balance_info = await calculate_balance(member["id"])
        total_collected += balance_info["amount_paid"]
        if balance_info["balance"] > 0:
            total_outstanding += balance_info["balance"]
        total_points += member.get("points", 0)
    
    average_points = total_points / total_members if total_members > 0 else 0
    
    return ReportsSummary(
        total_members=total_members,
        total_collected=total_collected,
        total_outstanding=total_outstanding,
        active_members=active_members,
        pending_members=pending_members,
        total_points_distributed=total_points,
        average_points_per_member=round(average_points, 1)
    )

# Rewards Management Routes
@api_router.get("/rewards", response_model=List[Reward])
async def get_rewards(
    active: Optional[bool] = None,
    category: Optional[RewardCategory] = None
):
    """Get rewards catalog (public endpoint)"""
    filter_query = {}
    
    if active is not None:
        filter_query["is_active"] = active
    
    if category:
        filter_query["category"] = category
    
    rewards = await db.rewards.find(filter_query).sort("created_at", -1).to_list(None)
    for reward in rewards:
        clean_mongo_doc(reward)
    return [Reward(**reward) for reward in rewards]

@api_router.post("/rewards", response_model=Reward)
async def create_reward(
    reward_data: RewardCreate,
    current_user: User = Depends(require_admin_or_staff)
):
    """Create a new reward (admin only)"""
    reward = Reward(**reward_data.dict())
    await db.rewards.insert_one(reward.dict())
    return reward

@api_router.put("/rewards/{reward_id}", response_model=Reward)
async def update_reward(
    reward_id: str,
    reward_data: RewardUpdate,
    current_user: User = Depends(require_admin_or_staff)
):
    """Update reward (admin only)"""
    reward = await db.rewards.find_one({"id": reward_id})
    if not reward:
        raise HTTPException(status_code=404, detail="Reward not found")
    
    update_data = {k: v for k, v in reward_data.dict().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    if update_data:
        await db.rewards.update_one({"id": reward_id}, {"$set": update_data})
    
    updated_reward = await db.rewards.find_one({"id": reward_id})
    clean_mongo_doc(updated_reward)
    return Reward(**updated_reward)

@api_router.put("/rewards/{reward_id}/toggle", response_model=Reward)
async def toggle_reward_active(
    reward_id: str,
    current_user: User = Depends(require_admin_or_staff)
):
    """Toggle reward active status (admin only)"""
    reward = await db.rewards.find_one({"id": reward_id})
    if not reward:
        raise HTTPException(status_code=404, detail="Reward not found")
    
    new_status = not reward.get("is_active", True)
    await db.rewards.update_one(
        {"id": reward_id},
        {"$set": {"is_active": new_status, "updated_at": datetime.now(timezone.utc)}}
    )
    
    updated_reward = await db.rewards.find_one({"id": reward_id})
    clean_mongo_doc(updated_reward)
    return Reward(**updated_reward)

# Redemptions Routes
@api_router.post("/members/{member_id}/redemptions", response_model=RewardRedemption)
async def create_redemption(
    member_id: str,
    redemption_data: RedemptionCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a redemption request"""
    # Check if member exists
    member = await db.members.find_one({"id": member_id})
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    # Check if reward exists and is active
    reward = await db.rewards.find_one({"id": redemption_data.reward_id})
    if not reward:
        raise HTTPException(status_code=404, detail="Reward not found")
    
    if not reward.get("is_active", True):
        raise HTTPException(status_code=400, detail="Reward is not active")
    
    # Check stock
    if reward.get("stock", 0) <= 0:
        raise HTTPException(status_code=400, detail="Reward out of stock")
    
    # Check member has enough points
    if not await can_member_redeem(member_id, reward["cost_points"]):
        raise HTTPException(status_code=400, detail="Not enough points")
    
    # Anti-abuse: limit pending redemptions
    pending_count = await count_pending_redemptions(member_id)
    if pending_count >= 3:
        raise HTTPException(status_code=400, detail="Too many pending redemptions. Please wait for approval.")
    
    # Create redemption
    redemption = RewardRedemption(
        member_id=member_id,
        member_name=member["full_name"],
        reward_id=redemption_data.reward_id,
        reward_name=reward["name"],
        points_cost=reward["cost_points"],
        note=redemption_data.note,
        created_by=current_user.id if current_user.role in [UserRole.ADMIN, UserRole.STAFF] else None
    )
    
    await db.reward_redemptions.insert_one(redemption.dict())
    return redemption

@api_router.get("/members/{member_id}/redemptions", response_model=List[RewardRedemption])
async def get_member_redemptions(
    member_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get member's redemption history"""
    # Members can only see their own redemptions, admins can see any
    if current_user.role == UserRole.ADHERENT and current_user.id != member_id:
        # For adherent members, we need to check if they're viewing their own profile
        # This would require linking user accounts to members, for now allowing access
        pass
    
    redemptions = await db.reward_redemptions.find({"member_id": member_id}).sort("created_at", -1).to_list(None)
    for redemption in redemptions:
        clean_mongo_doc(redemption)
    return [RewardRedemption(**redemption) for redemption in redemptions]

@api_router.get("/redemptions", response_model=List[RewardRedemption])
async def get_all_redemptions(
    status: Optional[RedemptionStatus] = None,
    current_user: User = Depends(require_admin_or_staff)
):
    """Get all redemptions (admin only)"""
    filter_query = {}
    if status:
        filter_query["status"] = status
    
    redemptions = await db.reward_redemptions.find(filter_query).sort("created_at", -1).to_list(None)
    for redemption in redemptions:
        clean_mongo_doc(redemption)
    return [RewardRedemption(**redemption) for redemption in redemptions]

@api_router.put("/redemptions/{redemption_id}/approve", response_model=RewardRedemption)
async def approve_redemption(
    redemption_id: str,
    status_update: RedemptionStatusUpdate,
    current_user: User = Depends(require_admin_or_staff)
):
    """Approve a redemption (admin only)"""
    redemption = await db.reward_redemptions.find_one({"id": redemption_id})
    if not redemption:
        raise HTTPException(status_code=404, detail="Redemption not found")
    
    if redemption["status"] != RedemptionStatus.PENDING:
        raise HTTPException(status_code=400, detail="Redemption already processed")
    
    # Check member still has enough points
    member_id = redemption["member_id"]
    points_cost = redemption["points_cost"]
    
    if not await can_member_redeem(member_id, points_cost):
        raise HTTPException(status_code=400, detail="Member no longer has enough points")
    
    # Check reward stock
    reward = await db.rewards.find_one({"id": redemption["reward_id"]})
    if not reward or reward.get("stock", 0) <= 0:
        raise HTTPException(status_code=400, detail="Reward out of stock")
    
    # Atomic operations: deduct points, reduce stock, update status
    # Deduct points via points transaction
    await add_points_transaction(
        member_id=member_id,
        points=-points_cost,
        transaction_type="redeem",
        description=f"Échange: {redemption['reward_name']}",
        recorded_by=current_user.id,
        recorded_by_name=current_user.name
    )
    
    # Reduce stock
    await db.rewards.update_one(
        {"id": redemption["reward_id"]},
        {"$inc": {"stock": -1}, "$set": {"updated_at": datetime.now(timezone.utc)}}
    )
    
    # Update redemption status
    await db.reward_redemptions.update_one(
        {"id": redemption_id},
        {"$set": {
            "status": RedemptionStatus.APPROVED,
            "approved_by": current_user.id,
            "approved_by_name": current_user.name,
            "note": status_update.note or redemption.get("note"),
            "updated_at": datetime.now(timezone.utc)
        }}
    )
    
    updated_redemption = await db.reward_redemptions.find_one({"id": redemption_id})
    clean_mongo_doc(updated_redemption)
    return RewardRedemption(**updated_redemption)

@api_router.put("/redemptions/{redemption_id}/deliver", response_model=RewardRedemption)
async def deliver_redemption(
    redemption_id: str,
    status_update: RedemptionStatusUpdate,
    current_user: User = Depends(require_admin_or_staff)
):
    """Mark redemption as delivered (admin only)"""
    redemption = await db.reward_redemptions.find_one({"id": redemption_id})
    if not redemption:
        raise HTTPException(status_code=404, detail="Redemption not found")
    
    if redemption["status"] != RedemptionStatus.APPROVED:
        raise HTTPException(status_code=400, detail="Redemption must be approved first")
    
    await db.reward_redemptions.update_one(
        {"id": redemption_id},
        {"$set": {
            "status": RedemptionStatus.DELIVERED,
            "delivered_by": current_user.id,
            "delivered_by_name": current_user.name,
            "note": status_update.note or redemption.get("note"),
            "updated_at": datetime.now(timezone.utc)
        }}
    )
    
    updated_redemption = await db.reward_redemptions.find_one({"id": redemption_id})
    clean_mongo_doc(updated_redemption)
    return RewardRedemption(**updated_redemption)

@api_router.put("/redemptions/{redemption_id}/reject", response_model=RewardRedemption)
async def reject_redemption(
    redemption_id: str,
    status_update: RedemptionStatusUpdate,
    current_user: User = Depends(require_admin_or_staff)
):
    """Reject a redemption (admin only)"""
    redemption = await db.reward_redemptions.find_one({"id": redemption_id})
    if not redemption:
        raise HTTPException(status_code=404, detail="Redemption not found")
    
    if redemption["status"] in [RedemptionStatus.DELIVERED, RedemptionStatus.REJECTED]:
        raise HTTPException(status_code=400, detail="Cannot reject delivered or already rejected redemption")
    
    # If already approved, need to refund points and stock
    if redemption["status"] == RedemptionStatus.APPROVED:
        member_id = redemption["member_id"]
        points_cost = redemption["points_cost"]
        
        # Refund points
        await add_points_transaction(
            member_id=member_id,
            points=points_cost,
            transaction_type="refund",
            description=f"Remboursement: {redemption['reward_name']} (échange rejeté)",
            recorded_by=current_user.id,
            recorded_by_name=current_user.name
        )
        
        # Restore stock
        await db.rewards.update_one(
            {"id": redemption["reward_id"]},
            {"$inc": {"stock": 1}, "$set": {"updated_at": datetime.now(timezone.utc)}}
        )
    
    await db.reward_redemptions.update_one(
        {"id": redemption_id},
        {"$set": {
            "status": RedemptionStatus.REJECTED,
            "note": status_update.note or redemption.get("note"),
            "updated_at": datetime.now(timezone.utc)
        }}
    )
    
    updated_redemption = await db.reward_redemptions.find_one({"id": redemption_id})
    clean_mongo_doc(updated_redemption)
    return RewardRedemption(**updated_redemption)

# Levels & Badges Routes
@api_router.get("/levels", response_model=List[Level])
async def get_levels():
    """Get all levels"""
    levels = await db.levels.find().sort("min_points", 1).to_list(None)
    for level in levels:
        clean_mongo_doc(level)
    return [Level(**level) for level in levels]

@api_router.post("/levels", response_model=Level)
async def create_level(
    level_data: LevelCreate,
    current_user: User = Depends(require_admin_or_staff)
):
    """Create a new level (admin only)"""
    level = Level(**level_data.dict())
    await db.levels.insert_one(level.dict())
    return level

@api_router.get("/badges", response_model=List[Badge])
async def get_badges():
    """Get all badges"""
    badges = await db.badges.find().sort("created_at", -1).to_list(None)
    for badge in badges:
        clean_mongo_doc(badge)
    return [Badge(**badge) for badge in badges]

@api_router.post("/badges", response_model=Badge)
async def create_badge(
    badge_data: BadgeCreate,
    current_user: User = Depends(require_admin_or_staff)
):
    """Create a new badge (admin only)"""
    # Check if badge code already exists
    existing = await db.badges.find_one({"code": badge_data.code})
    if existing:
        raise HTTPException(status_code=400, detail="Badge code already exists")
    
    badge = Badge(**badge_data.dict())
    await db.badges.insert_one(badge.dict())
    return badge

@api_router.get("/members/{member_id}/level", response_model=MemberLevel)
async def get_member_level_info(
    member_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get member's level information"""
    member = await db.members.find_one({"id": member_id})
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    return await get_member_level(member_id)

@api_router.get("/members/{member_id}/badges", response_model=List[MemberBadge])
async def get_member_badges_info(
    member_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get member's badges"""
    member = await db.members.find_one({"id": member_id})
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    return await get_member_badges(member_id)

@api_router.post("/members/{member_id}/badges/{badge_code}")
async def award_badge_to_member_manual(
    member_id: str,
    badge_code: str,
    current_user: User = Depends(require_admin_or_staff)
):
    """Manually award a badge to a member (admin only)"""
    member = await db.members.find_one({"id": member_id})
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    success = await award_badge_to_member(member_id, badge_code, current_user.id)
    if success:
        return {"message": f"Badge {badge_code} awarded successfully"}
    else:
        raise HTTPException(status_code=400, detail="Badge not found or already awarded")

# Leaderboard Routes
@api_router.get("/leaderboard", response_model=LeaderboardResponse)
async def get_leaderboard(
    period: str = "all_time",  # "monthly:YYYY-MM" or "all_time"
    limit: int = 50
):
    """Get leaderboard for specified period"""
    
    # Validate period format
    if period != "all_time" and not period.startswith("monthly:"):
        raise HTTPException(status_code=400, detail="Invalid period format. Use 'all_time' or 'monthly:YYYY-MM'")
    
    # Get leaderboard entries
    entries = await db.leaderboards.find({"period": period}).sort("rank", 1).limit(limit).to_list(None)
    
    leaderboard_entries = []
    for entry in entries:
        clean_mongo_doc(entry)
        leaderboard_entries.append(LeaderboardEntry(**entry))
    
    total_entries = await db.leaderboards.count_documents({"period": period})
    
    return LeaderboardResponse(
        period=period,
        entries=leaderboard_entries,
        total_entries=total_entries,
        generated_at=datetime.now(timezone.utc)
    )

@api_router.post("/leaderboard/generate/{year}/{month}")
async def generate_monthly_leaderboard(
    year: int,
    month: int,
    current_user: User = Depends(require_admin_or_staff)
):
    """Generate monthly leaderboard (admin only)"""
    if not (1 <= month <= 12):
        raise HTTPException(status_code=400, detail="Invalid month")
    
    if year < 2020 or year > 2030:
        raise HTTPException(status_code=400, detail="Invalid year")
    
    await build_monthly_leaderboard(year, month)
    return {"message": f"Monthly leaderboard generated for {year}-{month:02d}"}

@api_router.post("/leaderboard/generate/all-time")
async def generate_all_time_leaderboard(
    current_user: User = Depends(require_admin_or_staff)
):
    """Generate all-time leaderboard (admin only)"""
    await build_all_time_leaderboard()
    return {"message": "All-time leaderboard generated"}

# Daily job endpoint (for testing - in production this would be a cron job)
@api_router.post("/jobs/daily")
async def run_daily_jobs(
    current_user: User = Depends(require_admin_or_staff)
):
    """Run daily maintenance jobs (admin only)"""
    
    # Check and award regular payer badges for all members
    members = await db.members.find().to_list(None)
    badges_awarded = 0
    
    for member in members:
        try:
            await check_and_award_regular_payer_badge(member["id"])
            badges_awarded += 1
        except Exception as e:
            print(f"Error checking badges for member {member['id']}: {e}")
    
    # Rebuild all-time leaderboard
    await build_all_time_leaderboard()
    
    return {
        "message": "Daily jobs completed",
        "members_checked": len(members), 
        "badges_processed": badges_awarded
    }

# Initialize default data
@api_router.post("/init-data")
async def initialize_data():
    # Create default admin user
    admin_exists = await db.users.find_one({"email": "admin@amicale.ma"})
    if not admin_exists:
        admin_user = User(
            name="Administrator",
            email="admin@amicale.ma",
            role=UserRole.ADMIN
        )
        admin_dict = admin_user.dict()
        admin_dict["password_hash"] = hash_password("admin123")
        await db.users.insert_one(admin_dict)
    
    # Create default project types
    default_project_types = [
        {"name": "Logement", "default_due": 1500.0},
        {"name": "Micro-crédit", "default_due": 1000.0},
        {"name": "Éducation", "default_due": 800.0},
        {"name": "Santé", "default_due": 1200.0},
        {"name": "Autre", "default_due": 500.0}
    ]
    
    for pt_data in default_project_types:
        existing = await db.project_types.find_one({"name": pt_data["name"]})
        if not existing:
            project_type = ProjectType(
                name=pt_data["name"],
                default_due=pt_data["default_due"]
            )
            await db.project_types.insert_one(project_type.dict())
    
    # Create default rewards
    default_rewards = [
        {
            "name": "Carte cadeau 50 MAD", 
            "category": "Reductions", 
            "description": "Carte cadeau utilisable dans nos partenaires",
            "cost_points": 100,
            "stock": 20,
            "image_url": "https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=200&h=150&fit=crop"
        },
        {
            "name": "T-shirt Amicale Anouar", 
            "category": "Materiel", 
            "description": "T-shirt officiel avec logo de l'association",
            "cost_points": 80,
            "stock": 15,
            "image_url": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=200&h=150&fit=crop"
        },
        {
            "name": "Consultation gratuite", 
            "category": "Services", 
            "description": "Consultation gratuite avec nos experts",
            "cost_points": 150,
            "stock": 10,
            "image_url": "https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=200&h=150&fit=crop"
        },
        {
            "name": "Réduction 20% cotisation", 
            "category": "Reductions", 
            "description": "Réduction de 20% sur votre prochaine cotisation",
            "cost_points": 200,
            "stock": 25,
            "image_url": "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=200&h=150&fit=crop"
        },
        {
            "name": "Carnet de notes Amicale", 
            "category": "Materiel", 
            "description": "Carnet de notes avec couverture personnalisée",
            "cost_points": 60,
            "stock": 30,
            "image_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&h=150&fit=crop"
        },
        {
            "name": "Accès prioritaire événements", 
            "category": "Privileges", 
            "description": "Accès prioritaire aux événements de l'association",
            "cost_points": 120,
            "stock": 12,
            "image_url": "https://images.unsplash.com/photo-1511795409834-ef04bbd61622?w=200&h=150&fit=crop"
        },
        {
            "name": "Formation gratuite", 
            "category": "Services", 
            "description": "Participation gratuite à une formation au choix",
            "cost_points": 250,
            "stock": 8,
            "image_url": "https://images.unsplash.com/photo-1524178232363-1fb2b075b655?w=200&h=150&fit=crop"
        },
        {
            "name": "Pack Bienvenue", 
            "category": "Materiel", 
            "description": "Pack avec goodies de l'association",
            "cost_points": 90,
            "stock": 18,
            "image_url": "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=200&h=150&fit=crop"
        },
        {
            "name": "Invitation VIP", 
            "category": "Privileges", 
            "description": "Invitation VIP pour l'assemblée générale annuelle",
            "cost_points": 180,
            "stock": 5,
            "image_url": "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?w=200&h=150&fit=crop"
        },
        {
            "name": "Assistance personnalisée", 
            "category": "Services", 
            "description": "Service d'assistance personnalisée pour vos projets",
            "cost_points": 300,
            "stock": 6,
            "image_url": "https://images.unsplash.com/photo-1450101499163-c8848c66ca85?w=200&h=150&fit=crop"
        }
    ]
    
    for reward_data in default_rewards:
        existing = await db.rewards.find_one({"name": reward_data["name"]})
        if not existing:
            reward = Reward(**reward_data)
            await db.rewards.insert_one(reward.dict())
    
    # Create default levels
    default_levels = [
        {"name": "Bronze", "min_points": 0, "benefits": "Accès de base aux récompenses"},
        {"name": "Argent", "min_points": 51, "benefits": "Réductions supplémentaires sur les échanges"},
        {"name": "Or", "min_points": 201, "benefits": "Accès prioritaire aux événements"},
        {"name": "Platine", "min_points": 500, "benefits": "Avantages VIP et consultation gratuite"}
    ]
    
    for level_data in default_levels:
        existing = await db.levels.find_one({"name": level_data["name"]})
        if not existing:
            level = Level(**level_data)
            await db.levels.insert_one(level.dict())
    
    # Create default badges
    default_badges = [
        {
            "code": "REGULAR_PAYER",
            "name": "Payeur Régulier",
            "description": "3 mois consécutifs avec au moins un paiement",
            "image_url": "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=100&h=100&fit=crop"
        },
        {
            "code": "TOP_3_MONTH",
            "name": "Top 3 du Mois",
            "description": "Classé dans le top 3 mensuel",
            "image_url": "https://images.unsplash.com/photo-1534030347209-467a5b0ad3e6?w=100&h=100&fit=crop"
        },
        {
            "code": "FIRST_PAYMENT",
            "name": "Premier Paiement",
            "description": "Premier paiement effectué",
            "image_url": "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=100&h=100&fit=crop"
        },
        {
            "code": "BIG_SPENDER",
            "name": "Gros Échangeur",
            "description": "Plus de 500 points échangés",
            "image_url": "https://images.unsplash.com/photo-1607003417796-8412f036e09b?w=100&h=100&fit=crop"
        },
        {
            "code": "EARLY_ADOPTER",
            "name": "Utilisateur Précoce",
            "description": "Parmi les premiers membres de l'association",
            "image_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop"
        }
    ]
    
    for badge_data in default_badges:
        existing = await db.badges.find_one({"code": badge_data["code"]})
        if not existing:
            badge = Badge(**badge_data)
            await db.badges.insert_one(badge.dict())
    
    # Generate initial leaderboards
    try:
        current_date = datetime.now(timezone.utc)
        await build_monthly_leaderboard(current_date.year, current_date.month)
        await build_all_time_leaderboard()
    except Exception as e:
        print(f"Error generating initial leaderboards: {e}")
    
    return {"message": "Default data initialized with rewards, levels, badges and leaderboards"}

# Include router
app.include_router(api_router)

# CORS middleware
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