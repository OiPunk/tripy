from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from tripy.api.deps import get_locale
from tripy.core.i18n import t
from tripy.db.session import get_db

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live")
def liveness(locale: str = Depends(get_locale)) -> dict[str, str]:
    return {"status": t("health.ok", locale)}


@router.get("/ready")
def readiness(db: Session = Depends(get_db), locale: str = Depends(get_locale)) -> dict[str, str]:
    db.execute(text("SELECT 1"))
    return {"status": t("health.ok", locale)}
