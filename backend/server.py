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
    
    return {"message": "Default data initialized"}

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