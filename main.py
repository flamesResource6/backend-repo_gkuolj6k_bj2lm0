import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Animal, Application, Story, Volunteer, Donation

app = FastAPI(title="Animal Home API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helpers

def to_public(doc: dict):
    if not doc:
        return doc
    doc["id"] = str(doc.get("_id"))
    doc.pop("_id", None)
    return doc

# Seed some example data if empty (for demo UX)
@app.on_event("startup")
def seed_data():
    try:
        if db is None:
            return
        if db["animal"].count_documents({}) == 0:
            examples = [
                {
                    "name": "Luna",
                    "species": "dog",
                    "breed": "Labrador Mix",
                    "age": 3,
                    "size": "large",
                    "gender": "female",
                    "description": "Playful, gentle, loves long walks and belly rubs.",
                    "photos": [
                        "https://images.unsplash.com/photo-1543466835-00a7907e9de1?q=80&w=1200&auto=format&fit=crop"
                    ],
                    "featured": True,
                    "location": "Shelter A",
                    "good_with_kids": True,
                    "good_with_pets": True,
                },
                {
                    "name": "Milo",
                    "species": "cat",
                    "breed": "Tabby",
                    "age": 2,
                    "size": "medium",
                    "gender": "male",
                    "description": "Calm cuddle buddy who enjoys sunny windows.",
                    "photos": [
                        "https://images.unsplash.com/photo-1518791841217-8f162f1e1131?q=80&w=1200&auto=format&fit=crop"
                    ],
                    "featured": True,
                    "location": "Shelter B",
                    "good_with_kids": True,
                    "good_with_pets": False,
                },
                {
                    "name": "Poppy",
                    "species": "rabbit",
                    "breed": "Mini Rex",
                    "age": 1,
                    "size": "small",
                    "gender": "female",
                    "description": "Curious and gentle, loves greens.",
                    "photos": [
                        "https://images.unsplash.com/photo-1452857297128-d9c29adba80b?q=80&w=1200&auto=format&fit=crop"
                    ],
                    "featured": False,
                    "location": "Foster Home",
                },
            ]
            db["animal"].insert_many(examples)
        if db["story"].count_documents({}) == 0:
            db["story"].insert_many([
                {
                    "title": "Luna found her forever home",
                    "animal_name": "Luna",
                    "content": "After weeks of training and love, Luna is now hiking every weekend with her new family!",
                    "image_url": "https://images.unsplash.com/photo-1548199973-03cce0bbc87b?q=80&w=1200&auto=format&fit=crop",
                },
                {
                    "title": "Milo the office cat",
                    "animal_name": "Milo",
                    "content": "Milo helps his adopter debug code and nap responsibly.",
                    "image_url": "https://images.unsplash.com/photo-1511044568932-338cba0ad803?q=80&w=1200&auto=format&fit=crop",
                },
            ])
    except Exception:
        # Ignore seeding errors to avoid startup crash
        pass

# Routes
@app.get("/")
def health():
    return {"message": "Animal Home API running"}

@app.get("/animals")
def list_animals(
    q: Optional[str] = Query(None, description="Search by name or breed"),
    species: Optional[str] = Query(None, description="dog, cat, rabbit, bird, other"),
    age_min: Optional[int] = Query(None, ge=0),
    age_max: Optional[int] = Query(None, ge=0),
    size: Optional[str] = Query(None, description="small, medium, large, xlarge"),
    featured: Optional[bool] = Query(None),
    limit: int = Query(24, ge=1, le=100),
):
    if db is None:
        # fallback: empty list so frontend still loads
        return []
    filt = {}
    if q:
        filt["$or"] = [
            {"name": {"$regex": q, "$options": "i"}},
            {"breed": {"$regex": q, "$options": "i"}},
            {"description": {"$regex": q, "$options": "i"}},
        ]
    if species:
        filt["species"] = species
    if size:
        filt["size"] = size
    if featured is not None:
        filt["featured"] = featured
    age_query = {}
    if age_min is not None:
        age_query["$gte"] = age_min
    if age_max is not None:
        age_query["$lte"] = age_max
    if age_query:
        filt["age"] = age_query

    docs = db["animal"].find(filt).limit(limit)
    return [to_public(d) for d in docs]

@app.get("/animals/featured")
def featured_animals():
    if db is None:
        return []
    docs = db["animal"].find({"featured": True}).limit(8)
    return [to_public(d) for d in docs]

@app.post("/applications")
def submit_application(payload: Application):
    try:
        app_id = create_document("application", payload)
        return {"id": app_id, "status": "received"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/volunteers")
def submit_volunteer(payload: Volunteer):
    try:
        vid = create_document("volunteer", payload)
        return {"id": vid, "status": "received"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/donations")
def submit_donation(payload: Donation):
    try:
        did = create_document("donation", payload)
        return {"id": did, "status": "pledged"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stories")
def get_stories(limit: int = 6):
    if db is None:
        return []
    docs = db["story"].find({}).limit(limit)
    return [to_public(d) for d in docs]

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
