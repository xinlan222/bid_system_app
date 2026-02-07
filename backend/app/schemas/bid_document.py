"""Bid document schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class BidDocumentBase(BaseModel):
    """Base bid document schema."""

    original_filename: str = Field(..., description="Original filename of uploaded file")
    file_type: str = Field(..., description="MIME type of the file")
    project_name: str | None = Field(None, description="Project name (optional)")
    bidder_name: str | None = Field(None, description="Bidder name (optional)")


class BidDocumentCreate(BidDocumentBase):
    """Schema for creating a new bid document."""

    pass


class BidDocumentUpdate(BaseModel):
    """Schema for updating a bid document."""

    project_name: str | None = None
    bidder_name: str | None = None


class BidDocumentResponse(BaseModel):
    """Schema for bid document response."""

    id: UUID
    filename: str
    original_filename: str
    file_size: int
    file_type: str
    project_name: str | None
    bidder_name: str | None
    analysis_status: str
    analysis_result: dict | None
    uploaded_at: datetime
    analyzed_at: datetime | None

    class Config:
        from_attributes = True


class BidDocumentAnalysis(BaseModel):
    """Schema for bid document analysis result."""

    # Document metadata
    document_id: UUID
    filename: str

    # Extracted key information
    project_name: str | None = None
    project_number: str | None = None
    bidding_agency: str | None = None
    bid_deadline: datetime | None = None
    submission_deadline: datetime | None = None
    bid_bond_amount: str | None = None

    # Requirements
    qualification_requirements: list[str] = []
    technical_requirements: list[str] = []
    business_requirements: list[str] = []

    # Assessment criteria
    assessment_criteria: list[str] = []

    # Risk assessment
    risk_points: list[str] = []
    risk_level: str = "low"  # low, medium, high

    # Recommendations
    recommendations: list[str] = []

    # Summary
    summary: str
