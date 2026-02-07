"""Bid document service for file processing and AI analysis."""

import os
from pathlib import Path
from uuid import UUID, uuid4
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.bid_document import BidDocument
from app.repositories.bid_document import BidDocumentRepository


class BidDocumentService:
    """Service for bid document operations."""

    def __init__(self, session: AsyncSession, upload_dir: str = "uploads") -> None:
        """Initialize service.

        Args:
            session: Database session
            upload_dir: Directory for uploaded files
        """
        self.session = session
        self.repo = BidDocumentRepository(session)
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def upload_file(
        self,
        file_content: bytes,
        original_filename: str,
        file_type: str,
        user_id: UUID,
        project_name: str | None = None,
        bidder_name: str | None = None,
    ) -> BidDocument:
        """Upload and store a bid document.

        Args:
            file_content: File content as bytes
            original_filename: Original filename
            file_type: MIME type
            user_id: User ID
            project_name: Optional project name
            bidder_name: Optional bidder name

        Returns:
            Created bid document
        """
        # Generate unique filename
        file_ext = Path(original_filename).suffix
        filename = f"{uuid4()}{file_ext}"
        file_path = self.upload_dir / filename

        # Save file
        file_path.write_bytes(file_content)

        # Create database record
        doc = await self.repo.create(
            user_id=user_id,
            filename=filename,
            original_filename=original_filename,
            file_path=str(file_path),
            file_size=len(file_content),
            file_type=file_type,
            project_name=project_name,
            bidder_name=bidder_name,
        )

        return doc

    async def extract_text_from_file(self, doc: BidDocument) -> str:
        """Extract text content from a document file.

        Args:
            doc: Bid document

        Returns:
            Extracted text content
        """
        file_path = Path(doc.file_path)
        file_ext = file_path.suffix.lower()

        content = ""

        try:
            if file_ext == ".txt":
                # Plain text
                content = file_path.read_text(encoding="utf-8", errors="ignore")

            elif file_ext in [".pdf"]:
                # PDF extraction
                try:
                    import PyPDF2
                    reader = PyPDF2.PdfReader(str(file_path))
                    for page in reader.pages:
                        text = page.extract_text()
                        if text:
                            content += text + "\n"
                except Exception as e:
                    content = f"PDF 提取失败: {str(e)}"

            elif file_ext in [".doc", ".docx"]:
                # Word document extraction
                try:
                    if file_ext == ".docx":
                        import docx
                        doc_obj = docx.Document(str(file_path))
                        for para in doc_obj.paragraphs:
                            content += para.text + "\n"
                    else:
                        content = "旧版 .doc 文件暂不支持，请转换为 .docx"
                except Exception as e:
                    content = f"Word 文档提取失败: {str(e)}"

            else:
                content = f"不支持的文件类型: {file_ext}"

            # Update document with extracted text
            if content.strip():
                await self.repo.update_content_text(doc, content.strip())

        except Exception as e:
            content = f"文件读取错误: {str(e)}"

        return content.strip()

    def get_file_path(self, doc: BidDocument) -> Path:
        """Get file path for a document.

        Args:
            doc: Bid document

        Returns:
            File path
        """
        return Path(doc.file_path)

    async def delete_file(self, doc: BidDocument) -> None:
        """Delete a document and its file.

        Args:
            doc: Bid document
        """
        # Delete file from disk
        file_path = self.get_file_path(doc)
        if file_path.exists():
            file_path.unlink()

        # Delete from database
        await self.repo.delete(doc)
