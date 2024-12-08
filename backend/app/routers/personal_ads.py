from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime
from geopy.distance import geodesic

from app.models.user import User, PersonalAd
from app.schemas.user import PersonalAdCreate, PersonalAdResponse, PersonalAdUpdate
from app.routers.user import get_current_user

router = APIRouter(prefix="/personal-ads", tags=["personal-ads"])

@router.post("/", response_model=PersonalAdResponse)
async def create_personal_ad(
    ad_data: PersonalAdCreate,
    current_user: User = Depends(get_current_user)
):
    if not current_user.latitude or not current_user.longitude:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User location not set"
        )

    personal_ad = PersonalAd.create(
        user=current_user,
        content=ad_data.content,
        latitude=current_user.latitude,
        longitude=current_user.longitude
    )
    return personal_ad

@router.get("/", response_model=List[PersonalAdResponse])
async def get_personal_ads(
    distance: Optional[float] = None,
    current_user: User = Depends(get_current_user)
):
    query = PersonalAd.select().where(PersonalAd.is_active == True)
    
    if distance is not None:
        if not current_user.latitude or not current_user.longitude:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User location not set"
            )
        
        # Get all active ads and filter by distance
        ads = list(query)
        filtered_ads = []
        user_location = (current_user.latitude, current_user.longitude)
        
        for ad in ads:
            ad_location = (ad.latitude, ad.longitude)
            ad_distance = geodesic(user_location, ad_location).miles
            if ad_distance <= distance:
                filtered_ads.append(ad)
        
        return filtered_ads
    
    return list(query)

@router.get("/{ad_id}", response_model=PersonalAdResponse)
async def get_personal_ad(
    ad_id: int,
    current_user: User = Depends(get_current_user)
):
    try:
        ad = PersonalAd.get(
            (PersonalAd.id == ad_id) & 
            (PersonalAd.is_active == True)
        )
        return ad
    except PersonalAd.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personal ad not found"
        )

@router.put("/{ad_id}", response_model=PersonalAdResponse)
async def update_personal_ad(
    ad_id: int,
    ad_update: PersonalAdUpdate,
    current_user: User = Depends(get_current_user)
):
    try:
        ad = PersonalAd.get(
            (PersonalAd.id == ad_id) & 
            (PersonalAd.user == current_user)
        )
    except PersonalAd.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personal ad not found"
        )

    if ad_update.content is not None:
        ad.content = ad_update.content
    
    if ad_update.is_active is not None:
        ad.is_active = ad_update.is_active
    
    ad.updated_at = datetime.now()
    ad.save()
    return ad

@router.delete("/{ad_id}")
async def delete_personal_ad(
    ad_id: int,
    current_user: User = Depends(get_current_user)
):
    try:
        ad = PersonalAd.get(
            (PersonalAd.id == ad_id) & 
            (PersonalAd.user == current_user)
        )
    except PersonalAd.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personal ad not found"
        )

    ad.is_active = False
    ad.save()
    return {"message": "Personal ad deleted successfully"}

@router.get("/user/{user_id}", response_model=List[PersonalAdResponse])
async def get_user_personal_ads(
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    ads = PersonalAd.select().where(
        (PersonalAd.user_id == user_id) & 
        (PersonalAd.is_active == True)
    )
    return list(ads)
