import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from supabase import create_client, Client

# --- Configuration ---
# It is highly recommended to set these in Render's "Environment Variables" tab!
URL = os.getenv("SUPABASE_URL", "https://bdrwzxqucaefpwxyjqvv.supabase.co")
KEY = os.getenv("SUPABASE_KEY", "sb_publishable_rpTK6BCBOdUZC8O5TKIbcw_gAtloIGs")
SECRET_BEARER_TOKEN = os.getenv("API_TOKEN", "password")

supabase: Client = create_client(URL, KEY)
security = HTTPBearer()

app = FastAPI(
    title="Bookstore API", 
    description="Relational Database CRUD with Supabase",
    docs_url="/docs"
)

# --- Middleware ---
# This allows your browser (Swagger UI) to communicate with your Render server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Schemas ---
class BookBase(BaseModel):
    title: str
    author: str
    isbn: str
    published_year: int
    is_available: bool = True

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    is_available: Optional[bool] = None

# --- Security Dependency ---
async def verify_token(auth: HTTPAuthorizationCredentials = Depends(security)):
    """
    Validates the Bearer token. 
    In Swagger UI, click the 'Authorize' button and enter your password.
    """
    if auth.credentials != SECRET_BEARER_TOKEN:
        raise HTTPException(
            status_code=403, 
            detail="Invalid or missing Bearer Token"
        )
    return auth.credentials

# --- Routes ---

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/books", response_model=List[dict])
def get_books():
    response = supabase.table("books").select("*").execute()
    return response.data

@app.post("/books", status_code=201)
def create_book(book: BookCreate, token: str = Depends(verify_token)):
    # .model_dump() is the Pydantic v2 replacement for .dict()
    response = supabase.table("books").insert(book.model_dump()).execute()
    return response.data

@app.put("/books/{book_id}")
def update_book(book_id: int, book: BookCreate, token: str = Depends(verify_token)):
    response = supabase.table("books").update(book.model_dump()).eq("id", book_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Book not found")
    return response.data

@app.patch("/books/{book_id}")
def patch_book(book_id: int, book: BookUpdate, token: str = Depends(verify_token)):
    update_data = {k: v for k, v in book.model_dump().items() if v is not None}
    response = supabase.table("books").update(update_data).eq("id", book_id).execute()
    return response.data

@app.delete("/books/{book_id}")
def delete_book(book_id: int, token: str = Depends(verify_token)):
    response = supabase.table("books").delete().eq("id", book_id).execute()
    return {"message": f"Book {book_id} deleted"}
