from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.analytics_service import AnalyticsService
from app.models.schemas.analytics_schemas import AnalyticsOverviewResponse

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

@router.get("/overview/{user_id}", response_model=AnalyticsOverviewResponse)
async def get_overview(user_id: str, db: AsyncSession = Depends(get_db)):
    """Get high-level analytics for a user."""
    svc = AnalyticsService(db)
    try:
        overview = await svc.get_overview(user_id)
        return AnalyticsOverviewResponse(overview=overview)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
