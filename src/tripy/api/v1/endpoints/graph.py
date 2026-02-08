from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from tripy.api.deps import get_current_user, get_locale, require_permissions
from tripy.core.config import get_settings
from tripy.core.i18n import t
from tripy.db.models import User
from tripy.schemas.graph import GraphRequest, GraphResponse
from tripy.services.graph_service import GraphService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/graph", tags=["graph"])
service = GraphService()


@router.post("/execute", response_model=GraphResponse)
def execute_graph(
    payload: GraphRequest,
    _: None = Depends(require_permissions("graph:execute")),
    current_user: User = Depends(get_current_user),
    locale: str = Depends(get_locale),
) -> GraphResponse:
    settings = get_settings()
    passenger_id = current_user.passenger_id or settings.default_passenger_id

    try:
        assistant, thread_id, interrupted = service.execute(
            user_input=payload.user_input,
            thread_id=payload.thread_id,
            passenger_id=passenger_id,
            interrupt_message=t("graph.interrupt_confirmation", locale),
        )
    except Exception as exc:
        logger.exception("graph execution failed")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=t("graph.unavailable", locale),
        ) from exc

    return GraphResponse(assistant=assistant, thread_id=thread_id, interrupted=interrupted)
