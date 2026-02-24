from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from database import get_db
from models import Sale, User
from schemas import DashboardStats, ChartData
from auth import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Filter by user if Attendant
    query = db.query(Sale)
    if current_user.role == "Attendant":
        query = query.filter(Sale.user_id == current_user.id)
    
    sales = query.all()
    
    total_revenue = sum(sale.amount for sale in sales)
    total_liters = sum(sale.liters for sale in sales)
    petrol_liters = sum(sale.liters for sale in sales if sale.fuel_type == "petrol")
    diesel_liters = sum(sale.liters for sale in sales if sale.fuel_type == "diesel")
    
    return {
        "total_revenue": total_revenue,
        "total_liters": total_liters,
        "petrol_liters": petrol_liters,
        "diesel_liters": diesel_liters,
        "total_sales_count": len(sales)
    }

@router.get("/chart-data", response_model=ChartData)
def get_chart_data(
    days: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get data for last N days
    start_date = datetime.utcnow() - timedelta(days=days)
    
    query = db.query(Sale).filter(Sale.date >= start_date)
    if current_user.role == "Attendant":
        query = query.filter(Sale.user_id == current_user.id)
    
    sales = query.all()
    
    # Group by date
    daily_totals = {}
    for i in range(days):
        date = (datetime.utcnow() - timedelta(days=days-1-i)).strftime("%Y-%m-%d")
        daily_totals[date] = 0
    
    for sale in sales:
        date_str = sale.date.strftime("%Y-%m-%d")
        if date_str in daily_totals:
            daily_totals[date_str] += sale.amount
    
    return {
        "labels": list(daily_totals.keys()),
        "data": list(daily_totals.values())
    }