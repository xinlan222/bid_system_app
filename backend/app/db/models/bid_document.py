"""Bid document model."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text, func, JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class BidDocument(Base):
    """Bid document model for storing uploaded bid files."""

    __tablename__ = "bid_documents"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )

    # File information
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[int] = mapped_column(nullable=False)  # in bytes
    file_type: Mapped[str] = mapped_column(String(100), nullable=False)  # mime type

    # Extracted content
    content_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Analysis results
    analysis_result: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    analysis_status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        nullable=False,
    )  # pending, analyzing, completed, failed

    # Metadata
    project_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    bidder_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Timestamps
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    analyzed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    def __repr__(self) -> str:
        return f"<BidDocument(id={self.id}, filename={self.original_filename}, status={self.analysis_status})>"
