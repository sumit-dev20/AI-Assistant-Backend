from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from app import chat, extract_text_from_response
from models import UserRegister, UserLogin
from database import users_collection, session_collection, messages_collection
from auth import hash_password, verify_password, create_access_token
from dependencies import get_current_user

app = FastAPI()


class ChatRequest(BaseModel):
    session_id: str
    chat_id: str
    message: str


@app.post("/register")
async def register(user: UserRegister):
    existing = await users_collection.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = hash_password(user.password)

    user_data = {"name": user.name, "email": user.email, "password": hashed_pw}

    await users_collection.insert_one(user_data)

    return {"message": "User registered successfully", "register": True}


@app.post("/login")
async def login(user: UserLogin):
    db_user = await users_collection.find_one({"email": user.email})

    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_access_token(
        {
            "user_id": str(db_user["_id"]),
            "email": db_user["email"],
            "user_name": str(db_user["name"]),
        }
    )

    return {"access_token": token, "token_type": "bearer", "login": True}


@app.get("/")
def home():
    return {"response": "server is live"}


@app.post("/chat")
async def chat_api(
    req: ChatRequest,
    user_id: str = Depends(get_current_user),
):
    print("user_id=>", user_id)
    raw_response = await chat(user_id, req.message, req.chat_id, req.session_id)

    clean_text = extract_text_from_response(raw_response)

    return {"response": clean_text}


@app.get("/chat_sessions")
async def get_chat_sessions(user_id: str = Depends(get_current_user)):
    print("user_id", user_id)
    cursor = session_collection.find({"user_id": user_id}).sort("updated_at", -1)

    sessions = await cursor.to_list(length=100)

    # Convert ObjectId to string
    for session in sessions:
        session["_id"] = str(session["_id"])

    return {"chat_sessions": sessions}


@app.get("/get_chats")
async def get_chats(session_id: str, user_id: str = Depends(get_current_user)):

    cursor = messages_collection.find(
        {"user_id": user_id, "session_id": session_id}
    ).sort("updated_at", -1)

    chats = await cursor.to_list(length=100)

    # Convert ObjectId to string
    for chat in chats:
        chat["_id"] = str(chat["_id"])

    return {"chats": chats}


@app.delete("/delete_chat")
async def delete_chat(session_id: str, user_id: str = Depends(get_current_user)):

    await session_collection.delete_one({"session_id": session_id, "user_id": user_id})

    await messages_collection.delete_many(
        {"session_id": session_id, "user_id": user_id}
    )

    return {"message": "Deleted Successfully"}
