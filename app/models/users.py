from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Enum, ForeignKey, UniqueConstraint
from app.core.db import Base
from app.utils.security import generate_short_id
from sqlalchemy.sql import func
import enum

class RoleEnum(str,enum.Enum):
  user = "enduser"
  admin = "admin"
  guide = "guide"
  

class GenderEnum(str,enum.Enum):
   male = "male"
   female = "Female"

class User(Base):
  __tablename__="user"


  id             = Column(Integer,primary_key=True, index=True)
  public_id      = Column(String(10), unique=True, default=lambda: generate_short_id(10), index=True, nullable=False)

  full_name      = Column(String, nullable=False)
  first_name     = Column(String, nullable=True)
  last_name      = Column(String, nullable=True)

  email          = Column(String, unique=True, index=True, nullable=False)
  password       = Column(String, nullable=False)

  role           = Column(Enum(RoleEnum, name="role_enum"), nullable=False, index=True, default=RoleEnum.user)

  avatar_url     = Column(String, nullable=True)
  phone          = Column(String, nullable=True)
  gender         = Column(Enum(GenderEnum, name="gender_enum"), nullable=True)
  date_of_birth  = Column(Date, nullable=True)
  address        = Column(String, nullable=True)

  is_active      = Column(Boolean, default=True, nullable=False)
  is_verified    = Column(Boolean, default=False, nullable=False)
  is_first_login = Column(Boolean, default=True, nullable=False)

  created_at     = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
  updated_at     = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

  def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} role={self.role}>"