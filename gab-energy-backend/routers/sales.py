from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Sale, User
from schemas import SaleCreate, SaleUpdate, SaleResponse
from auth import get_current_user, require_role

router = APIRouter(prefix="/api/sales", tags=["Sales"])

@router.get("/", response_model=List[SaleResponse])
def get_sales(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Attendants see only their sales, Managers see all
    if current_user.role == "Attendant":
        sales = db.query(Sale).filter(Sale.user_id == current_user.id).offset(skip).limit(limit).all()
    else:
        sales = db.query(Sale).offset(skip).limit(limit).all()
    
    return sales

@router.get("/{sale_id}", response_model=SaleResponse)
def get_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sale not found"
        )
    
    # Attendants can only view their own sales
    if current_user.role == "Attendant" and sale.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this sale"
        )
    
    return sale

@router.post("/", response_model=SaleResponse, status_code=status.HTTP_201_CREATED)
def create_sale(
    sale_data: SaleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    amount = sale_data.liters * sale_data.price
    
    new_sale = Sale(
        fuel_type=sale_data.fuel_type,
        liters=sale_data.liters,
        price=sale_data.price,
        amount=amount,
        user_id=current_user.id
    )
    
    db.add(new_sale)
    db.commit()
    db.refresh(new_sale)
    
    return new_sale

@router.put("/{sale_id}", response_model=SaleResponse)
def update_sale(
    sale_id: int,
    sale_data: SaleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sale not found"
        )
    
    # Attendants can only edit their own sales
    if current_user.role == "Attendant" and sale.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to edit this sale"
        )
    
    sale.fuel_type = sale_data.fuel_type
    sale.liters = sale_data.liters
    sale.price = sale_data.price
    sale.amount = sale_data.liters * sale_data.price
    
    db.commit()
    db.refresh(sale)
    
    return sale