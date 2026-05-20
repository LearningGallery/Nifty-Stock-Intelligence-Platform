"""
Document Upload Models
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from enum import Enum


class DocumentType(str, Enum):
    ANNUAL_REPORT = "annual_report"
    QUARTERLY_REPORT = "quarterly_report"
    INVESTOR_PRESENTATION = "investor_presentation"
    ANALYST_REPORT = "analyst_report"
    OTHER = "other"


class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    status: ProcessingStatus
    message: str
    s3_location: str
    uploaded_at: datetime


class DocumentStatus(BaseModel):
    document_id: str
    filename: str
    status: ProcessingStatus
    progress: int  # 0-100
    total_pages: Optional[int] = None
    chunks_created: Optional[int] = None
    error_message: Optional[str] = None
    processed_at: Optional[datetime] = None
    stock_symbol: Optional[str] = None
