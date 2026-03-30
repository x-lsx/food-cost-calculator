from slugify import slugify
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status, HTTPException
from typing import List, Optional

from app.models.business import Business
from app.models.user import User

from ..schemas.business import BusinessCreate, BusinessUpdate, BusinessResponse
from ..repositories.business import BusinessRepository


class BusinessService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.business_repository = BusinessRepository(db)

    async def _generate_slug(
        self,
        name: str,
    ) -> str:
        base_slug = slugify(name)
        slug = base_slug
        index = 1
        while await self.business_repository.get_business_by_slug(slug):
            slug = f"{base_slug}-{index}"
            index += 1
        return slug

    async def get_business_by_name(
        self,
        user_id: int,
        page: int,
        size: int,
        search: Optional[str] = None,
    ) -> List[BusinessResponse]:

        if page < 1:
            page = 1
        if size < 1 or size > 20:
            size = 10

        offset = (page - 1) * size

        businesses = await self.business_repository.get_business_by_name(
            user_id=user_id,
            limit=size,
            offset=offset,
            search=search,
        )   

        return [BusinessResponse.model_validate(business) for business in businesses]

    async def get_business_by_id(
        self,
        business_id: int,
        user_id: int
    ) -> BusinessResponse:
        business = await self.business_repository.get_business_by_id_and_owner_id(business_id, user_id)
        if not business:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Business not found")
        return BusinessResponse.model_validate(business)

    async def get_business_by_slug(
        self,
        business_slug: str,
    ) -> BusinessResponse:
        business = await self.business_repository.get_business_by_slug(business_slug)
        if not business:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Business not found")
        return BusinessResponse.model_validate(business)
    
    async def create_business(
        self,
        business_data: BusinessCreate,
        current_user: User,
    ) -> BusinessResponse:
        
        existing_business = await self.business_repository.get_business_by_name_and_owner_id(
            name=business_data.name,
            owner_id=current_user.id
        )
        if existing_business:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Business with this name already exists for the owner"
            )
        slug = await self._generate_slug(business_data.name)
        
        new_business_data = business_data.model_dump()
        new_business_data["owner_id"] = current_user.id
        new_business_data["slug"] = slug
        new_business = await self.business_repository.create_business(new_business_data)
        
        return BusinessResponse.model_validate(new_business)

    async def update_business(self,
        business: Business,
        update_data: BusinessUpdate,
        ) -> BusinessResponse:
        
        business = await self.business_repository.get_business_by_id(business.id)
        
        if not business:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business not found"
            )
        
        if update_data.name and update_data.name != business.name:
            name_exists = await self.business_repository.get_business_by_name_and_owner_id(
                name=update_data.name,
                owner_id=business.owner_id
            )
            if name_exists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Бизнес с таким именем уже существует для этого владельца"
                )
                
            new_slug = await self._generate_slug(update_data.name)
            
            update_dict = update_data.model_dump(exclude_unset=True)
            update_dict["slug"] = new_slug
        else:
            update_dict = update_data.model_dump(exclude_unset=True)
               
        updated_business = await self.business_repository.update_business(
            business_id=business.id,
            update_data=update_dict,
        )
        
        return BusinessResponse.model_validate(updated_business)
