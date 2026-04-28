from pydantic import BaseModel
from typing import List

from app.schemas.ml_product_performance_schema import MLProductPerformanceItem


class SemanticTriple(BaseModel):
    subject: str
    predicate: str
    object: str | int | float | None


class SemanticProductPerformanceItem(MLProductPerformanceItem):
    semantic_triples: List[SemanticTriple]
    semantic_explanation: str


class SemanticProductPerformanceResponse(BaseModel):
    items: List[SemanticProductPerformanceItem]


class ProductPerformanceOntologyResponse(BaseModel):
    ontology_file: str
    ontology: dict
    sample_triples: List[SemanticTriple]
