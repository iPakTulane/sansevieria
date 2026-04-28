from __future__ import annotations

import json
from pathlib import Path

from app.schemas.ml_product_performance_schema import MLProductPerformanceItem
from app.schemas.semantic_product_performance_schema import (
    SemanticProductPerformanceItem,
    SemanticTriple,
)


MODEL_NAME = "ProductPerformanceClassifier"
ONTOLOGY_PATH = (
    Path(__file__).resolve().parent.parent
    / "ontology"
    / "sansevieria_product_performance.jsonld"
)


def _normalize_class_name(value: str) -> str:
    return " ".join((value or "").strip().lower().split())


def build_product_performance_triples(item: MLProductPerformanceItem) -> list[SemanticTriple]:
    # Assignment note:
    # These are lightweight RDF-style triples represented as JSON objects.
    # We intentionally keep this plain Python/JSON-LD (no external graph database).
    subject = f"Product_{item.product_id}"
    metric_subject = f"MetricSnapshot_Product_{item.product_id}"
    prediction_subject = f"Prediction_Product_{item.product_id}"

    return [
        SemanticTriple(subject=subject, predicate="hasPerformanceClass", object=item.performance_class),
        SemanticTriple(subject=subject, predicate="belongsToCategory", object=item.product_category or "Uncategorized"),
        SemanticTriple(subject=subject, predicate="hasMetricSnapshot", object=metric_subject),
        SemanticTriple(subject=metric_subject, predicate="hasUnitsSold", object=item.units_sold),
        SemanticTriple(subject=metric_subject, predicate="hasRevenue", object=item.revenue),
        SemanticTriple(subject=metric_subject, predicate="hasOrdersCount", object=item.orders_count),
        SemanticTriple(subject=prediction_subject, predicate="hasConfidence", object=item.confidence),
        SemanticTriple(subject=prediction_subject, predicate="hasExplanation", object=item.explanation),
        SemanticTriple(subject=prediction_subject, predicate="generatedByModel", object=MODEL_NAME),
    ]


def build_semantic_explanation(item: MLProductPerformanceItem) -> str:
    return (
        f"Semantic classification: Product_{item.product_id} hasPerformanceClass "
        f"'{item.performance_class}' generatedByModel '{MODEL_NAME}', with metrics "
        f"units={item.units_sold}, revenue={item.revenue:.2f}, orders={item.orders_count}."
    )


def enrich_with_semantics(items: list[MLProductPerformanceItem]) -> list[SemanticProductPerformanceItem]:
    return [
        SemanticProductPerformanceItem(
            **item.model_dump(),
            semantic_triples=build_product_performance_triples(item),
            semantic_explanation=build_semantic_explanation(item),
        )
        for item in items
    ]


def filter_by_performance_class(
    items: list[SemanticProductPerformanceItem], class_name: str | None
) -> list[SemanticProductPerformanceItem]:
    if not class_name:
        return items
    expected = _normalize_class_name(class_name)
    return [item for item in items if _normalize_class_name(item.performance_class) == expected]


def get_product_performance_ontology() -> dict:
    # JSON-LD ontology metadata for Assignment 5 semantic layer demonstration.
    with ONTOLOGY_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)
