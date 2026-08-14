# built in imports
from fastapi import FastAPI
from contextlib import asynccontextmanager

# custom imports
from app.routes.auth.user_auth import router as auth_router
from app.core.mongo_db import client, otps_collection


@asynccontextmanager
async def lifespan(app : FastAPI):
  # TTL index — 10 min baad auto delete
  await otps_collection.create_index(
      "created_at",
      expireAfterSeconds=600
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


# register auth route
app.include_router(auth_router)


@app.get("/")
async def get_me():
  return {"hello" : "server"}