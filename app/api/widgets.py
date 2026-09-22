from app.schemas.widget_config import WidgetConfigResponse
from app.services.widget_config_service import get_public_widget_config
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_tenant
from app.db.session import get_db
from app.models.tenant import Tenant
from app.schemas.widget import WidgetCreate, WidgetResponse
from app.services.widget_service import (
    create_new_widget,
    get_widget,
    list_widgets,
    remove_widget,
)

router = APIRouter(prefix="/widgets", tags=["Widgets"])


@router.get("", response_model=list[WidgetResponse])
def get_widgets(
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    return list_widgets(
        db=db,
        tenant_id=tenant.id,
    )


@router.get("/{widget_id}", response_model=WidgetResponse)
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Widget not found",
        )

    return widget


@router.post(
    "",
    response_model=WidgetResponse,
    status_code=status.HTTP_201_CREATED,
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


@router.delete("/{widget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(
    widget_id: int,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    deleted = remove_widget(
        db=db,
        widget_id=widget_id,
        tenant_id=tenant.id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Widget not found",
        )

    return None

@router.get(
    "/{widget_id}/config",
    response_model=WidgetConfigResponse,
)
def get_public_config(
    widget_id: int,
    db: Session = Depends(get_db),
):
    widget = get_public_widget_config(
        db=db,
        widget_id=widget_id,
    )

    if not widget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Widget not found or inactive",
        )

    return widget