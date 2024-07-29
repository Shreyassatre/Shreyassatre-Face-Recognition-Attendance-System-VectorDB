from fastapi import FastAPI
from .routes import users, admin

from .database import engine, Base

from .utils.auth_utils import get_password_hash

Base.metadata.create_all(bind=engine)

hasshed_pass = get_password_hash("admin")
print(hasshed_pass)

app = FastAPI()

app.include_router(users.router)
app.include_router(admin.router)








