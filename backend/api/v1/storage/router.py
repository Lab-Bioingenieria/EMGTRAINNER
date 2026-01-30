
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from typing import List, Dict, Any

from app.services.csv_service import csv_service

storage_router = APIRouter()

@storage_router.get("/sessions")
async def list_sessions() -> List[Dict[str, Any]]:
    """List all stored CSV sessions"""
    return csv_service.list_sessions()

@storage_router.get("/sessions/{filename:path}")
async def get_session_file(filename: str):
    """Download a specific session CSV file"""
    file_path = csv_service.get_session_path(filename)
    if not file_path:
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path, 
        filename=filename, 
        media_type='text/csv'
    )
