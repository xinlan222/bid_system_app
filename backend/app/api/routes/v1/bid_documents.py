"""Bid document API routes."""

import json
from uuid import UUID
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, DBSession
from app.db.models.bid_document import BidDocument
from app.db.models.user import User
from app.repositories.bid_document import BidDocumentRepository
from app.schemas.bid_document import (
    BidDocumentCreate,
    BidDocumentResponse,
    BidDocumentUpdate,
)
from app.services.bid_document import BidDocumentService

router = APIRouter()


@router.post("/upload", response_model=BidDocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_bid_document(
    file: UploadFile = File(...),
    project_name: str | None = None,
    bidder_name: str | None = None,
    current_user: User = Depends(CurrentUser),
    db: AsyncSession = Depends(DBSession),
) -> Any:
    """Upload a bid document for analysis.

    Args:
        file: Uploaded file (PDF, DOCX, TXT)
        project_name: Optional project name
        bidder_name: Optional bidder name
        current_user: Currently authenticated user
        db: Database session

    Returns:
        Created bid document
    """
    # Read file content
    file_content = await file.read()
    file_type = file.content_type or "application/octet-stream"

    # Create service and upload
    service = BidDocumentService(db)
    doc = await service.upload_file(
        file_content=file_content,
        original_filename=file.filename or "unknown",
        file_type=file_type,
        user_id=current_user.id,
        project_name=project_name,
        bidder_name=bidder_name,
    )

    return doc


@router.get("/{doc_id}", response_model=BidDocumentResponse)
async def get_bid_document(
    doc_id: UUID,
    current_user: User = Depends(CurrentUser),
    db: AsyncSession = Depends(DBSession),
) -> Any:
    """Get a bid document by ID.

    Args:
        doc_id: Document ID
        current_user: Currently authenticated user
        db: Database session

    Returns:
        Bid document
    """
    repo = BidDocumentRepository(db)
    doc = await repo.get_by_id(doc_id, current_user.id)

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    return doc


@router.get("", response_model=list[BidDocumentResponse])
async def list_bid_documents(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(CurrentUser),
    db: AsyncSession = Depends(DBSession),
) -> Any:
    """List all bid documents for current user.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        current_user: Currently authenticated user
        db: Database session

    Returns:
        List of bid documents
    """
    repo = BidDocumentRepository(db)
    docs = await repo.get_list_by_user(current_user.id, skip, limit)
    return docs


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bid_document(
    doc_id: UUID,
    current_user: User = Depends(CurrentUser),
    db: AsyncSession = Depends(DBSession),
) -> None:
    """Delete a bid document.

    Args:
        doc_id: Document ID
        current_user: Currently authenticated user
        db: Database session
    """
    repo = BidDocumentRepository(db)
    service = BidDocumentService(db)

    doc = await repo.get_by_id(doc_id, current_user.id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    await service.delete_file(doc)


@router.post("/{doc_id}/analyze", response_model=BidDocumentResponse)
async def analyze_bid_document(
    doc_id: UUID,
    current_user: User = Depends(CurrentUser),
    db: AsyncSession = Depends(DBSession),
) -> Any:
    """Analyze a bid document using AI.

    Args:
        doc_id: Document ID
        current_user: Currently authenticated user
        db: Database session

    Returns:
        Analyzed bid document
    """
    # Get document
    repo = BidDocumentRepository(db)
    doc = await repo.get_by_id(doc_id, current_user.id)

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # Extract text if not already done
    if not doc.content_text:
        service = BidDocumentService(db)
        await service.extract_text_from_file(doc)
        # Refresh doc from db
        doc = await repo.get_by_id(doc_id, current_user.id)

    # Check if OPENAI_API_KEY is configured
    from app.core.config import settings

    if not settings.OPENAI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OPENAI_API_KEY not configured. Please configure it in backend/.env",
        )

    # Update status to analyzing
    await repo.update_status(doc, "analyzing")

    try:
        # Import AI agent
        from app.agents.bid_analysis import bid_analysis_agent, BidAnalysisDeps

        # Create dependencies
        deps = BidAnalysisDeps(
            document_id=str(doc.id),
            filename=doc.original_filename,
        )

        # Run analysis
        result = await bid_analysis_agent.run(doc.content_text, deps=deps)

        # Parse result as JSON
        analysis_result = json.loads(result)

        # Update document with analysis result
        await repo.update_analysis(doc, analysis_result)

        # Refresh from db
        doc = await repo.get_by_id(doc_id, current_user.id)

    except Exception as e:
        # Update status to failed
        await repo.update_status(doc, "failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}",
        )

    return doc
