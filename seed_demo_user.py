#!/usr/bin/env python3
"""
Seed script to create a demo user for development/testing
Demo credentials: admin@example.com / admin123
"""

import sys
import os

sys.path.append(os.path.dirname(__file__))

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User
from app.models.enums import UserRole

db = SessionLocal()

try:
    # Check if demo user already exists
    demo_user = db.query(User).filter(User.email == "admin@example.com").first()
    
    if demo_user:
        print("✓ Demo user already exists: admin@example.com")
    else:
        # Create demo user
        new_user = User(
            name="Admin User",
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        print("✓ Demo user created successfully!")
        print(f"  Email: admin@example.com")
        print(f"  Password: admin123")
        print(f"  Role: {new_user.role}")
        print(f"  ID: {new_user.id}")

finally:
    db.close()
