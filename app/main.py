# built in imports
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

# custom imports
from app.routes.auth.user_auth import router as auth_router
from app.core.mongo_db import client, otps_collection, links_collection
from app.routes.url_routes.url_routes import router as url_router


@asynccontextmanager
async def lifespan(app : FastAPI):
  # TTL index — 10 min baad auto delete
  await otps_collection.create_index(
      "created_at",
      expireAfterSeconds=600
  )

  # Links TTL — expire hone ke 30 din baad delete
  await links_collection.create_index(
      "expires_at",
      expireAfterSeconds=2592000  # 30 days in seconds
  )
  
  # start up
  print("MongoDB connected ✅")
  yield
  # shutdown
  client.close()
  print("MongoDB disconnected ❌")



app = FastAPI(title="Snip Ly",
              description= "This Is Root App",
              debug=True, 
              version="1.0.0",
              lifespan= lifespan)


app.add_middleware(
  CORSMiddleware,
  allow_origins=["http://localhost:5173"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)


# register auth route
app.include_router(auth_router)

# register url route
app.include_router(url_router)


@app.get("/")
async def get_me():
  return {"hello" : "server"}