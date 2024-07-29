from fastapi import APIRouter, HTTPException, UploadFile, Body, Request
from typing import Annotated
from ..utils.attendance_utils import register_user, verify_user, get_username_by_id, log_attendance, read_image_data

router = APIRouter()

@router.post("/register")
async def register(request: Request, username: Annotated[str, Body()], image_data: UploadFile):
    try:
        ip_address = request.client.host
        
        img = await read_image_data(image_data)
        
        success, message = register_user(username, img, ip_address)
        if success:
            return {"message": message}
        else:
            raise HTTPException(status_code=400, detail=message)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.post("/mark-attendance")
async def mark_attendance(image_data: UploadFile):
    try:
        img = await read_image_data(image_data)

        success, user_id, similarity_score = verify_user(img)
        
        if success:
            username = get_username_by_id(user_id)
            if username:
                log_attendance(user_id, username)
                return {"user_id": user_id, "username": username, "similarity_score": similarity_score}
            else:
                return {"message": "User ID found but username not found in database"}
        elif similarity_score:
            return {"message": "User not recognized", "similarity_score": similarity_score}
        else:
            return {"message": "User not recognized"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

