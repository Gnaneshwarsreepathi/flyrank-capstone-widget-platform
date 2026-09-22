from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.deps import get_current_tenant
from app.db.session import get_db
from app.models.tenant import Tenant
from app.schemas.widget import WidgetCreate, WidgetResponse
from app.schemas.widget_config import WidgetConfigResponse
from app.services.widget_config_service import get_public_widget_config
from app.services.widget_service import (
    create_new_widget,
    get_widget,
    list_widgets,
    remove_widget,
    update_existing_widget,
)


router = APIRouter(
    prefix="/widgets",
    tags=["Widgets"],
)


# ---------------------------------------------------------
# Public widget configuration
# ---------------------------------------------------------

@router.get("/{widget_id}/config")
def get_public_config(
    widget_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    widget = get_public_widget_config(
        db=db,
        widget_id=widget_id,
    )

    if not widget:
        raise HTTPException(
            status_code=404,
            detail="Widget not found or inactive",
        )

    # ETag changes whenever the widget version changes.
    etag = f'"widget-{widget.id}-v{widget.version}"'

    headers = {
        "Cache-Control": "public, max-age=60, must-revalidate",
        "ETag": etag,
    }

    # Client already has the current version.
    if request.headers.get("if-none-match") == etag:
        return Response(
            status_code=304,
            headers=headers,
        )

    # Return the public widget configuration as JSON.
    config = WidgetConfigResponse.model_validate(widget)

    return Response(
        content=config.model_dump_json(),
        status_code=200,
        media_type="application/json",
        headers=headers,
    )


# ---------------------------------------------------------
# Tenant widget management
# ---------------------------------------------------------

@router.get(
    "",
    response_model=list[WidgetResponse],
)
def get_widgets(
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    return list_widgets(
        db=db,
        tenant_id=tenant.id,
    )


@router.get(
    "/{widget_id}",
    response_model=WidgetResponse,
)
def get_single_widget(
    widget_id: int,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    widget = get_widget(
        db=db,
        widget_id=widget_id,
        tenant_id=tenant.id,
    )

    if not widget:
        raise HTTPException(
            status_code=404,
            detail="Widget not found",
        )

    return widget


@router.post(
    "",
    response_model=WidgetResponse,
    status_code=201,
)
def create(
    request: WidgetCreate,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    return create_new_widget(
        db=db,
        tenant_id=tenant.id,
        widget_type=request.widget_type,
        title=request.title,
        description=request.description,
        form_fields=request.form_fields,
        button_text=request.button_text,
        display_options=request.display_options,
        is_active=request.is_active,
    )


@router.put(
    "/{widget_id}",
    response_model=WidgetResponse,
)
def update(
    widget_id: int,
    request: WidgetCreate,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    widget = get_widget(
        db=db,
        widget_id=widget_id,
        tenant_id=tenant.id,
    )

    if not widget:
        raise HTTPException(
            status_code=404,
            detail="Widget not found",
        )

    return update_existing_widget(
        db=db,
        widget=widget,
        widget_type=request.widget_type,
        title=request.title,
        description=request.description,
        form_fields=request.form_fields,
        button_text=request.button_text,
        display_options=request.display_options,
        is_active=request.is_active,
    )


@router.delete(
    "/{widget_id}",
    status_code=204,
)
def delete(
    widget_id: int,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    widget = get_widget(
        db=db,
        widget_id=widget_id,
        tenant_id=tenant.id,
    )

    if not widget:
        raise HTTPException(
            status_code=404,
            detail="Widget not found",
        )

    remove_widget(
        db=db,
        widget=widget,
    )

    return None