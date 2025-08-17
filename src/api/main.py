"""
FastAPI backend - clean REST API for frontend integration
Simple, pragmatic design with proper error handling
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging
import tempfile
import os
from datetime import datetime

from ..services import ExtractionService, ExportService
from ..models import JournalType


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
extraction_service = ExtractionService()
export_service = ExportService()

# FastAPI app
app = FastAPI(
    title="Paper Information Extractor API",
    description="Unified API for extracting information from academic papers (Nature, Science, APS)",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =================== Request/Response Models ===================

class ExtractionRequest(BaseModel):
    """Request model for paper extraction"""
    input_text: str = Field(..., description="Paper URL or title")
    journal_hint: Optional[str] = Field(None, description="Optional journal hint (nature, science, aps)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "input_text": "https://journals.aps.org/prxquantum/abstract/10.1103/PRXQuantum.6.010344",
                "journal_hint": "aps"
            }
        }


class ExportRequest(BaseModel):
    """Request model for export operations"""
    format: str = Field(..., description="Export format (excel, json, csv)")
    filename: Optional[str] = Field(None, description="Optional custom filename")
    
    class Config:
        json_schema_extra = {
            "example": {
                "format": "excel",
                "filename": "my_paper.xlsx"
            }
        }


class APIResponse(BaseModel):
    """Standard API response wrapper"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


# =================== API Endpoints ===================

@app.get("/", response_model=Dict[str, str])
async def root():
    """API health check and info"""
    return {
        "message": "Paper Information Extractor API",
        "version": "1.0.0",
        "status": "healthy",
        "supported_journals": ", ".join(extraction_service.get_supported_journals())
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now()}


@app.get("/journals", response_model=Dict[str, Any])
async def get_supported_journals():
    """Get information about supported journals"""
    try:
        journals_info = extraction_service.get_extractor_info()
        return APIResponse(
            success=True,
            data={
                "supported_journals": extraction_service.get_supported_journals(),
                "extractors": journals_info
            }
        ).dict()
    
    except Exception as e:
        logger.error(f"Error getting journals info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/extract", response_model=APIResponse)
async def extract_paper(request: ExtractionRequest):
    """
    Extract paper information from URL or title
    
    Main extraction endpoint - handles all journal types
    """
    try:
        logger.info(f"Extraction request: {request.input_text[:100]}...")
        
        # Perform extraction
        result = extraction_service.extract_paper(
            input_text=request.input_text,
            journal_hint=request.journal_hint
        )
        
        if result.success:
            return APIResponse(
                success=True,
                data=result.to_dict()
            )
        else:
            return APIResponse(
                success=False,
                error=result.error
            )
    
    except Exception as e:
        logger.error(f"Extraction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/extract/batch", response_model=List[APIResponse])
async def extract_papers_batch(requests: List[ExtractionRequest]):
    """
    Batch extraction for multiple papers
    
    Processes multiple extraction requests efficiently
    """
    results = []
    
    for req in requests:
        try:
            result = extraction_service.extract_paper(
                input_text=req.input_text,
                journal_hint=req.journal_hint
            )
            
            if result.success:
                response = APIResponse(success=True, data=result.to_dict())
            else:
                response = APIResponse(success=False, error=result.error)
            
            results.append(response)
            
        except Exception as e:
            logger.error(f"Batch extraction error for {req.input_text}: {e}")
            results.append(APIResponse(success=False, error=str(e)))
    
    return results


@app.post("/export/{paper_id}")
async def export_paper(
    paper_id: str,
    export_request: ExportRequest,
    background_tasks: BackgroundTasks
):
    """
    Export paper data to specified format
    
    Note: This is a simplified example. In production, you'd store
    extracted papers and reference them by ID.
    """
    # This is a placeholder implementation
    # In a real system, you'd retrieve the paper by ID from storage
    
    return APIResponse(
        success=False,
        error="Export endpoint requires implementation of paper storage"
    )


@app.get("/search/{journal}")
async def search_journal(journal: str, title: str):
    """
    Search specific journal for papers by title
    
    Args:
        journal: Journal type (nature, science, aps)
        title: Paper title to search for
    """
    try:
        # Validate journal type
        if journal.lower() not in extraction_service.get_supported_journals():
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported journal: {journal}"
            )
        
        result = extraction_service.extract_paper(
            input_text=title,
            journal_hint=journal
        )
        
        if result.success:
            return APIResponse(success=True, data=result.to_dict())
        else:
            return APIResponse(success=False, error=result.error)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_extraction_stats():
    """Get API usage statistics"""
    # Placeholder for statistics
    # In production, implement proper metrics collection
    
    return {
        "total_extractions": "Not implemented",
        "success_rate": "Not implemented",
        "popular_journals": "Not implemented",
        "note": "Statistics collection not implemented in this demo"
    }


# =================== Error Handlers ===================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return APIResponse(
        success=False,
        error=f"HTTP {exc.status_code}: {exc.detail}"
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return APIResponse(
        success=False,
        error="Internal server error"
    )


# =================== Utility Functions ===================

def cleanup_temp_files():
    """Background task to clean up temporary export files"""
    # Implement cleanup logic for exported files
    pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)