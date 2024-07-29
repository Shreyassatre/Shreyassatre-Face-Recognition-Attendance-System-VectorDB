from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from ..database import User as UserModel
from ..schema import UserInDB, UserAdminView
from ..utils.auth_utils import get_current_user, get_db, authenticate_user, create_access_token
import os
import pandas as pd

router = APIRouter()

@router.get("/admin/users/", tags=["admin"], response_model=List[UserAdminView])
async def list_users(user_id: Optional[int] = None, current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    if user_id is not None:
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return [user]

    return db.query(UserModel).filter(current_user.id != UserModel.id).all()

@router.post("/login", tags=["auth"], include_in_schema=False)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=15)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/admin/attendance/{date}", tags=["admin"])
async def get_attendance(date: str, current_user: UserInDB = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    file_path = f"attendance_sheets/{date}.xlsx"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attendance sheet not found")

    try:
        attendance_data = pd.read_excel(file_path)
        return attendance_data.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error reading attendance sheet: {str(e)}")

@router.get("/admin/attendance-sheets/", tags=["admin"])
async def list_attendance_sheets(current_user: UserInDB = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    try:
        files = os.listdir("attendance_sheets/")
        attendance_sheets = [f for f in files if f.endswith(".xlsx")]
        all_sheets = []

        for sheet in attendance_sheets:
            try:
                file_path = f"attendance_sheets/{sheet}"
                attendance_data = pd.read_excel(file_path)
                all_sheets.append({
                    "date": sheet.split('.')[0],
                    "data": attendance_data.to_dict(orient="records")
                })
            except ValueError:
                continue

        return {"attendance_sheets": all_sheets}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error listing attendance sheets: {str(e)}")

@router.get("/admin/attendance-sheets-range/", tags=["admin"])
async def list_attendance_sheets_range(
    start_date: str = Query(..., description="Start date in DD-MM-YYYY format"),
    end_date: str = Query(..., description="End date in DD-MM-YYYY format"),
    current_user: UserInDB = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    try:
        start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        files = os.listdir("attendance_sheets/")
        attendance_sheets = [f for f in files if f.endswith(".xlsx")]
        filtered_sheets = []

        for sheet in attendance_sheets:
            try:
                sheet_date = datetime.strptime(sheet.split('.')[0], '%Y-%m-%d')
                if start_date_dt <= sheet_date <= end_date_dt:
                    file_path = f"attendance_sheets/{sheet}"
                    attendance_data = pd.read_excel(file_path)
                    filtered_sheets.append({
                        "date": sheet.split('.')[0],
                        "data": attendance_data.to_dict(orient="records")
                    })
            except ValueError:
                continue
        
        if not filtered_sheets:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No attendance sheets found in the specified date range")

        return {"attendance_sheets": filtered_sheets}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error filtering attendance sheets: {str(e)}")