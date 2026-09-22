"""Pydantic request models for the API."""
from typing import Any, Optional
from pydantic import BaseModel, Field


class CreateDatabaseReq(BaseModel):
    name: str
    type: str = "normal"  # normal | vector


class RenameDatabaseReq(BaseModel):
    name: str


class FilterCondition(BaseModel):
    field: str
    operator: str
    value: Optional[Any] = None


class FilterGroup(BaseModel):
    logic: str = "AND"  # AND | OR
    conditions: list[FilterCondition] = Field(default_factory=list)


class RecordBody(BaseModel):
    data: Optional[dict] = None  # allow raw object via Request in router


class DeleteIdsReq(BaseModel):
    ids: list[str] = Field(default_factory=list)


class VectorizeReq(BaseModel):
    docIds: list[str] = Field(default_factory=list)
    model: Optional[str] = None
    chunkSize: int = 500
    overlap: int = 20


class RetrievalReq(BaseModel):
    query: str
    topK: Optional[int] = None
    threshold: Optional[float] = None


class VectorConfigReq(BaseModel):
    model: str
    chunkSize: int = 500
    chunkOverlap: int = 20
    topK: int = 10
    similarityThreshold: float = 0.3
