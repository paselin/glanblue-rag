"""
Pydantic models for API requests and responses.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ElementType(str, Enum):
    """Element types in Granblue Fantasy."""
    FIRE = "火"
    WATER = "水"
    EARTH = "土"
    WIND = "風"
    LIGHT = "光"
    DARK = "闇"


class RarityType(str, Enum):
    """Character/Weapon rarity."""
    SSR = "SSR"
    SR = "SR"
    R = "R"


class DocumentType(str, Enum):
    """Types of documents in the knowledge base."""
    CHARACTER = "character"
    WEAPON = "weapon"
    SUMMON = "summon"
    QUEST = "quest"
    PARTY_COMPOSITION = "party_composition"


# Chat API Models
class ChatMessage(BaseModel):
    """Chat message model."""
    role: str = Field(..., description="Message role: user or assistant")
    content: str = Field(..., description="Message content")
    timestamp: Optional[datetime] = None


class UserContext(BaseModel):
    """User context information."""
    user_rank: Optional[int] = Field(None, ge=1, le=400, description="User rank")
    owned_characters: Optional[List[str]] = Field(default_factory=list)
    owned_weapons: Optional[List[str]] = Field(default_factory=list)
    favorite_element: Optional[ElementType] = None


class ChatRequest(BaseModel):
    """Chat API request."""
    message: str = Field(..., min_length=1, max_length=1000)
    context: Optional[UserContext] = None
    conversation_id: Optional[str] = None


class Source(BaseModel):
    """Information source reference."""
    type: DocumentType
    name: str
    url: Optional[str] = None
    relevance_score: float = Field(..., ge=0.0, le=1.0)


class ChatResponse(BaseModel):
    """Chat API response."""
    response: str
    sources: List[Source] = Field(default_factory=list)
    suggested_actions: List[str] = Field(default_factory=list)
    conversation_id: str


# Search API Models
class SearchFilters(BaseModel):
    """Search filter options."""
    type: Optional[DocumentType] = None
    element: Optional[ElementType] = None
    rarity: Optional[RarityType] = None
    tags: Optional[List[str]] = None


class SearchRequest(BaseModel):
    """Search API request."""
    query: str = Field(..., min_length=1)
    filters: Optional[SearchFilters] = None
    top_k: int = Field(default=10, ge=1, le=50)


class SearchResult(BaseModel):
    """Single search result."""
    id: str
    type: DocumentType
    name: str
    content: str
    metadata: Dict[str, Any]
    score: float


class SearchResponse(BaseModel):
    """Search API response."""
    results: List[SearchResult]
    total: int
    query: str


# Document Models
class DocumentMetadata(BaseModel):
    """Document metadata."""
    rarity: Optional[RarityType] = None
    element: Optional[ElementType] = None
    weapon_type: Optional[str] = None
    tier: Optional[str] = None
    updated_at: datetime
    source_url: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class Document(BaseModel):
    """Knowledge base document."""
    id: str
    type: DocumentType
    name: str
    content: str
    metadata: DocumentMetadata
    chunk_index: int = 0


# Party Composition Models
class PartyMember(BaseModel):
    """Party member (character)."""
    name: str
    element: ElementType
    rarity: RarityType
    role: str = Field(..., description="Role in party: attacker, support, healer, etc.")
    is_required: bool = Field(default=False)
    alternatives: List[str] = Field(default_factory=list)


class PartyComposition(BaseModel):
    """Party composition model."""
    name: str
    objective: str
    element: ElementType
    members: List[PartyMember]
    weapons: Optional[List[str]] = None
    summons: Optional[List[str]] = None
    strategy: str
    difficulty: int = Field(..., ge=1, le=5)
    tags: List[str] = Field(default_factory=list)


# System Models
class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    timestamp: datetime
