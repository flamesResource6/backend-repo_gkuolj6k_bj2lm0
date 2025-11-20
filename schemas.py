"""
Database Schemas for Animal Home

Each Pydantic model represents a MongoDB collection. The collection name is the lowercase of the class name.
"""
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, EmailStr

# Animals available for adoption
class Animal(BaseModel):
    name: str = Field(..., description="Animal name")
    species: Literal["dog", "cat", "rabbit", "bird", "other"] = Field(..., description="Animal type/species")
    breed: Optional[str] = Field(None, description="Breed or mix")
    age: int = Field(..., ge=0, le=40, description="Age in years")
    size: Literal["small", "medium", "large", "xlarge"] = Field(..., description="Approximate size")
    gender: Optional[Literal["male", "female"]] = Field(None, description="Gender")
    description: Optional[str] = Field(None, description="Short bio/temperament")
    photos: List[str] = Field(default_factory=list, description="Image URLs")
    featured: bool = Field(default=False, description="Show in featured list")
    location: Optional[str] = Field(None, description="Shelter/city")
    good_with_kids: Optional[bool] = None
    good_with_pets: Optional[bool] = None

# Adoption applications
class Application(BaseModel):
    animal_id: str = Field(..., description="Target animal document id")
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    message: Optional[str] = None

# Success stories shared by the shelter
class Story(BaseModel):
    title: str
    animal_name: Optional[str] = None
    content: str
    image_url: Optional[str] = None

# Volunteer interest submissions
class Volunteer(BaseModel):
    full_name: str
    email: EmailStr
    interests: List[str] = Field(default_factory=list)
    availability: Optional[str] = None
    message: Optional[str] = None

# Donation pledges (no payment processor in demo)
class Donation(BaseModel):
    full_name: str
    email: Optional[EmailStr] = None
    amount: float = Field(..., gt=0)
    message: Optional[str] = None
