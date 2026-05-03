import os
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, UploadFile
from uuid import UUID
from sqlalchemy.exc import IntegrityError

from app.schemas.commodities import CommodityCreate, CommodityUpdate, BulkInsertResponse
from app.repositories import commodities as commodity_repo
from app.utils.excel_parser import parse_commodities_excel
from app.models.users import User

UPLOAD_DIR = "app/public/image"
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def _save_image(file: UploadFile, commodity_id: UUID) -> str:
    file_extension = os.path.splitext(file.filename)[1]
    filename = f"{commodity_id}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
        
    return f"/{file_path}".replace("\\", "/")  # Normalize path for web

async def list_commodities(db: AsyncSession, skip: int = 0, limit: int = 20, search: str | None = None):
    return await commodity_repo.get_commodities(db, skip=skip, limit=limit, search=search)

async def insert_commodity(db: AsyncSession, commodity: CommodityCreate, image: UploadFile | None, current_user: User):
    farmer_id = current_user.id
        
    try:
        db_commodity = await commodity_repo.create_commodity(db, commodity, farmer_id)
        
        if image:
            path_image = await _save_image(image, db_commodity.id)
            # Update the commodity with the new path
            db_commodity = await commodity_repo.update_commodity(db, db_commodity, CommodityUpdate(path_image=path_image))
            
        return db_commodity
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Database integrity error: {str(e.orig)}")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

async def update_catalog(db: AsyncSession, commodity_id: UUID, commodity_update: CommodityUpdate, image: UploadFile | None, current_user: User):
    farmer_id = current_user.id
    
    db_commodity = await commodity_repo.get_commodity_by_id(db, commodity_id)
    if not db_commodity:
        raise HTTPException(status_code=404, detail="Commodity not found")
        
    if db_commodity.farmer_id != farmer_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this commodity")
        
    if image:
        path_image = await _save_image(image, commodity_id)
        commodity_update.path_image = path_image
        
    try:
        return await commodity_repo.update_commodity(db, db_commodity, commodity_update)
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Database integrity error: {str(e.orig)}")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

async def bulk_insert_excel(db: AsyncSession, file: UploadFile, current_user: User) -> BulkInsertResponse:
    farmer_id = current_user.id
        
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Only Excel files (.xlsx, .xls) are supported")
        
    content = await file.read()
    
    try:
        valid_data, errors = parse_commodities_excel(content, farmer_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        await file.close()
        
    if errors:
        return BulkInsertResponse(
            success=False,
            inserted_count=0,
            errors=errors
        )
        
    if not valid_data:
        raise HTTPException(status_code=400, detail="Excel file is empty or contains no valid data")
        
    try:
        inserted_count = await commodity_repo.bulk_create_commodities(db, valid_data)
        await db.commit()
        return BulkInsertResponse(
            success=True,
            inserted_count=inserted_count,
            errors=[]
        )
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Database error during bulk insert: {str(e.orig)}")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
