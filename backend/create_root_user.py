from database import SessionLocal, engine
import models
from auth import get_password_hash

def create_root_user():
    # Create tables if they don't exist
    models.Base.metadata.drop_all(bind=engine)  # Drop existing tables
    models.Base.metadata.create_all(bind=engine)  # Create new tables
    
    db = SessionLocal()
    try:
        # Check if root user already exists
        existing_user = db.query(models.User).filter(
            (models.User.email == "sunahn76@gmail.com") | 
            (models.User.username == "root")
        ).first()
        
        if existing_user:
            print("Root user already exists!")
            return
        
        # Create root user
        root_user = models.User(
            email="sunahn76@gmail.com",
            username="root",
            hashed_password=get_password_hash("rootpassword"),
            is_active=True,
            is_admin=True
        )
        
        db.add(root_user)
        db.commit()
        print("Root user created successfully!")
        
    except Exception as e:
        print(f"Error creating root user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_root_user() 