from slugify import slugify
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status, HTTPException
from typing import List, Optional

from ..repositories.packaging import PackagingRepository
from ..schemas.packaging import PackagingCreate, PackagingResponse, PackagingUpdate


class PackagingService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = PackagingRepository(db)

    async def get_by_id(
        self,
        business_id: int,
        packaging_id: int,
    ) -> Optional[PackagingResponse]:
        packaging = await self.repo.get_by_id(packaging_id)
        if not packaging or packaging.business_id != business_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Packaging not found."
            )
        return PackagingResponse.model_validate(packaging)

    async def list_by_business_id(
        self,
        business_id: int,
        page: int,
        size: int,
        search: Optional[str] = None,
    ) -> List[PackagingResponse]:

        if page < 1:
            page = 1
        if size < 1 or size > 20:
            size = 10

        offset = (page - 1) * size
        packigings = await self.repo.list(business_id, search, size, offset)
        return [PackagingResponse.model_validate(pack) for pack in packigings]

    async def create(
        self,
        business_id: int,
        schema: PackagingCreate,
    ) -> PackagingResponse:
        if await self.repo.name_exists(business_id, schema.name):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Упаковка с названием '{schema.name}' уже существует."
            )
        create_data = schema.model_dump()
        create_data["business_id"] = business_id
        new_packaging = await self.repo.create(create_data)
        return PackagingResponse.model_validate(new_packaging)

    async def update(
        self,
        business_id: int,
        packaging_id: int,
        schema: PackagingUpdate,
    ) -> PackagingResponse:
        packaging = await self.repo.get_by_id_for_business(packaging_id, business_id)
        if not packaging:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The package was not found or you do not have access."
            )
        update_data = schema.model_dump(exclude_unset=True)
        if not update_data:
            return PackagingResponse.model_validate(packaging)  

        updated_packaging = await self.repo.update(
            packaging_id=packaging_id,
            update_data=update_data
        )

        return PackagingResponse.model_validate(updated_packaging)
    
    async def delete(
        self,
        business_id: int,
        packaging_id: int,
    ) -> None:
        deleted = await self.repo.delete(business_id, packaging_id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Упаковка не найдена или у вас нет доступа."
            )