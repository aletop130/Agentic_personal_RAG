from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class DocumentUpload(BaseModel):
    filename: str = Field(..., description="Name of the uploaded file")
    file_type: str = Field(..., description="Type of document (pdf, docx, txt)")
    file_size: int = Field(..., description="Size of file in bytes")


class DocumentResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    file_size: int
    uploaded_at: datetime
    chunk_count: int
    status: str


class ChatMessage(BaseModel):
    role: str = Field(..., description="Role of the message (user, assistant, system)")
    content: str = Field(..., description="Content of the message")


class ChatRequest(BaseModel):
    message: str = Field(..., description="User's message")
    conversation_history: List[ChatMessage] = Field(default_factory=list, description="Previous messages in the conversation")
    top_k: Optional[int] = Field(default=5, description="Number of relevant chunks to retrieve")


class ToolCall(BaseModel):
    id: str
    type: str
    function: Dict[str, str]


class ChatResponse(BaseModel):
    message: str
    sources: Optional[List[Dict[str, Any]]] = None
    tool_calls: Optional[List[ToolCall]] = None


class StreamChunk(BaseModel):
    type: str = Field(..., description="Type of chunk (content, tool_call, error)")
    content: Optional[str] = None
    tool_call: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    qdrant_connected: bool
    regolo_connected: bool


class DeleteResponse(BaseModel):
    success: bool
    message: str
