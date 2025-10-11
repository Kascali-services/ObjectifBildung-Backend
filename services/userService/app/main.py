from fastapi import FastAPI
from app.routes.user_routes import router
from app.db.database import Base, engine

app = FastAPI(title="UserService")

Base.metadata.create_all(bind=engine)
app.include_router(router)
