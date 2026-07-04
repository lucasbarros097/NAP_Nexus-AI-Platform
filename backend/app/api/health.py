"""Health check and system information endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.config import settings
from app.core.database import get_session

router = APIRouter(tags=["health"])


@router.get("/system")
async def system_info():
    """Return system configuration info (non-sensitive)."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "model": settings.OPENROUTER_MODEL,
        "debug": settings.DEBUG,
    }


@router.get("/db")
async def db_health(db: AsyncSession = Depends(get_session)):
    """Check database connectivity."""
    try:
        result = await db.execute(text("SELECT 1 AS healthy"))
        row = result.scalar_one()
        return {"database": "connected", "healthy": row == 1}
    except Exception as e:
        return {"database": "error", "detail": str(e)}