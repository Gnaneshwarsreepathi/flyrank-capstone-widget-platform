from sqlalchemy.orm import Session

from app.repositories.submission_repository import (
    count_submissions_by_tenant,
    get_submissions_by_tenant,
)


def get_dashboard_data(
    db: Session,
    tenant_id: int,
    limit: int = 50,
):
    total_submissions = count_submissions_by_tenant(
        db=db,
        tenant_id=tenant_id,
    )

    submissions = get_submissions_by_tenant(
        db=db,
        tenant_id=tenant_id,
        limit=limit,
    )

    return {
        "total_submissions": total_submissions,
        "submissions": submissions,
    }