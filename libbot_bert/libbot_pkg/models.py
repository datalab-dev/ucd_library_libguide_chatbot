from pydantic import BaseModel, Field


# ---- Request ----

class QueryRequest(BaseModel):
    query: str = Field(..., description="The user's search query.")
    top_k: int = Field(default=3, ge=1, le=20, description="Number of unique results to return.")


# ---- Response ----

class Source(BaseModel):
    """A single guide/section where a result text was found."""
    libguide_title: str
    section_title: str
    url: str


class SearchResult(BaseModel):
    """One deduplicated result, potentially found across multiple guides."""
    score: float = Field(..., description="Cosine similarity score (higher is better).")
    text: str = Field(..., description="The retrieved text chunk.")
    sources: list[Source] = Field(..., description="All guides this text appeared in.")


class QueryResponse(BaseModel):
    query: str
    top_k: int
    results: list[SearchResult]