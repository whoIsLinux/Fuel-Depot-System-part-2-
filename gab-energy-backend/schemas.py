from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

# User Schemas
class UserBase(BaseModel):
    username: str
    role: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# Sale Schemas
class SaleBase(BaseModel):
    fuel_type: str = Field(..., pattern="^(petrol|diesel)$")
    liters: float = Field(..., gt=0)
    price: float = Field(..., gt=0)

class SaleCreate(SaleBase):
    pass

class SaleUpdate(SaleBase):
    pass

class SaleResponse(SaleBase):
    id: int
    amount: float
    date: datetime
    user_id: int
    
    class Config:
        from_attributes = True

# Dashboard Schemas
class DashboardStats(BaseModel):
    total_revenue: float
    total_liters: float
    petrol_liters: float
    diesel_liters: float
    total_sales_count: int

class ChartData(BaseModel):
    labels: List[str]
    data: List[float]