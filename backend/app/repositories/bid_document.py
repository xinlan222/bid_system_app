"""Bid document repository."""

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.bid_document import BidDocument


class BidDocumentRepository:
    """Repository for bid document database operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.

        Args:
            session: Async database session
        """
        self.session = session

    async def create(
        self,
        *,
        user_id: Any,
        filename: str,
        original_filename: str,
        file_path: str,
        file_size: int,
        file_type: str,
        project_name: str | None = None,
        bidder_name: str | None = None,
    ) -> BidDocument:
        """Create a new bid document.

        Args:
            user_id: User ID
            filename: Stored filename
            original_filename: Original filename
            file_path: File path
            file_size: File size in bytes
            file_type: MIME type
            project_name: Optional project name
            bidder_name: Optional bidder name

        Returns:
            Created bid document
        """
        doc = BidDocument(
            user_id=user_id,
            filename=filename,
            original_filename=original_filename,
            file_path=file_path,
            file_size=file_size,
            file_type=file_type,
            project_name=project_name,
            bidder_name=bidder_name,
        )
        self.session.add(doc)
        await self.session.flush()
        await self.session.refresh(doc)
        return doc

    async def get_by_id(self, doc_id: Any, user_id: Any) -> BidDocument | None:
        """Get a bid document by ID and user ID.

        Args:
            doc_id: Document ID
            user_id: User ID

        Returns:
            Bid document or None
        """
        result = await self.session.execute(
            select(BidDocument)
            .where(BidDocument.id == doc_id)
            .where(BidDocument.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_list_by_user(
        self,
        user_id: Any,
        skip: int = 0,
        limit: int = 100,
    ) -> list[BidDocument]:
        """Get list of bid documents for a user.

        Args:
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of bid documents
        """
        result = await self.session.execute(
            select(BidDocument)
            .where(BidDocument.user_id == user_id)
            .order_by(BidDocument.uploaded_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def update_content_text(
        self,
        doc: BidDocument,
        content_text: str,
    ) -> BidDocument:
        """Update document's extracted text content.

        Args:
            doc: Bid document to update
            content_text: Extracted text content

        Returns:
            Updated bid document
        """
        doc.content_text = content_text
        self.session.add(doc)
        await self.session.flush()
        await self.session.refresh(doc)
        return doc

    async def update_analysis(
        self,
        doc: BidDocument,
        analysis_result: dict,
    ) -> BidDocument:
        """Update document's analysis result.

        Args:
            doc: Bid document to update
            analysis_result: Analysis result JSON

        Returns:
            Updated bid document
        """
        doc.analysis_result = analysis_result
        doc.analysis_status = "completed"
        self.session.add(doc)
        await self.session.flush()
        await self.session.refresh(doc)
        return doc

    async def update_status(
        self,
        doc: BidDocument,
        status: str,
    ) -> BidDocument:
        """Update document's analysis status.

        Args:
            doc: Bid document to update
            status: New status (pending, analyzing, completed, failed)

        Returns:
            Updated bid document
        """
        doc.analysis_status = status
        self.session.add(doc)
        await self.session.flush()
        await self.session.refresh(doc)
        return doc

    async def delete(self, doc: BidDocument) -> None:
        """Delete a bid document.

        Args:
            doc: Bid document to delete
        """
        await self.session.delete(doc)
        await self.session.flush()
