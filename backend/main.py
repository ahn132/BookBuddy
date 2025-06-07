from datetime import timedelta
from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
import models
from database import engine, get_db
import auth
import os
import pdfplumber
import re
from collections import defaultdict

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

class UserCreate(BaseModel):
    email: str
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    email: str
    username: str
    is_active: bool
    is_admin: bool

    class Config:
        orm_mode = True

def get_current_admin(current_user: models.User = Depends(auth.get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

@app.post("/register", response_model=User)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=User)
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

@app.get("/admin/users", response_model=List[User])
def read_users(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@app.put("/admin/users/{user_id}/toggle-admin", response_model=User)
def toggle_admin_status(
    user_id: int,
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify your own admin status"
        )
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_admin = not user.is_admin
    db.commit()
    db.refresh(user)
    return user

def extract_chapters(pdf_path: str):
    """Extract chapters from PDF using pdfplumber for better font size detection."""
    chapters = []
    current_chapter = None
    current_content = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # Extract text with font information
            words = page.extract_words(
                keep_blank_chars=True,
                use_text_flow=True,
                horizontal_ltr=True,
                vertical_ttb=True,
                extra_attrs=['size', 'fontname']
            )
            
            # Group words into lines with their font information
            lines = []
            current_line = []
            current_y = None
            
            for word in words:
                if current_y is None:
                    current_y = word['top']
                elif abs(word['top'] - current_y) > 5:  # New line if y-position differs significantly
                    if current_line:
                        lines.append({
                            'text': ' '.join(w['text'] for w in current_line),
                            'size': max(w['size'] for w in current_line),
                            'font': current_line[0]['fontname']
                        })
                    current_line = []
                    current_y = word['top']
                current_line.append(word)
            
            if current_line:
                lines.append({
                    'text': ' '.join(w['text'] for w in current_line),
                    'size': max(w['size'] for w in current_line),
                    'font': current_line[0]['fontname']
                })
            
            # Process lines to detect chapters
            for line in lines:
                text = line['text'].strip()
                size = line['size']
                
                # Chapter detection patterns
                is_chapter = False
                if re.match(r'^(?:Chapter|CHAPTER)\s+\d+[^\n]*$', text):
                    is_chapter = True
                elif re.match(r'^\d+$', text) and size > 12:  # Standalone numbers with larger font
                    is_chapter = True
                
                if is_chapter:
                    # Save previous chapter if exists
                    if current_chapter:
                        chapters.append({
                            'title': current_chapter,
                            'content': '\n'.join(current_content)
                        })
                    current_chapter = text
                    current_content = []
                else:
                    if current_chapter:
                        current_content.append(text)
    
    # Add the last chapter
    if current_chapter:
        chapters.append({
            'title': current_chapter,
            'content': '\n'.join(current_content)
        })
    
    return chapters

@app.post("/admin/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_admin)
):
    """Upload a PDF file and parse its chapters."""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Create uploads directory if it doesn't exist
    os.makedirs("uploads", exist_ok=True)
    
    # Save the file
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    try:
        # Extract chapters
        chapters = extract_chapters(file_path)
        
        # Print chapter information
        print("\nExtracted Chapters:")
        for chapter in chapters:
            print(f"\nChapter: {chapter['title']}")
            print("Content preview:", chapter['content'][:200] + "...")
        
        return {"message": "PDF uploaded and parsed successfully", "chapters": chapters}
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")
    finally:
        # Clean up the uploaded file
        if os.path.exists(file_path):
            os.remove(file_path) 