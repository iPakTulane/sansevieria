from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session
import numpy as np
from sklearn.tree import DecisionTreeClassifier

from app.schemas.ml_product_performance_schema import MLProductPerformanceItem


def _to_float(value) -> float:
    if value is None:
        return 0.0
    return max(0.0, float(value))


def _to_int(value) -> int:
    if value is None:
        return 0
    return max(0, int(value))


def _safe_min_max_normalize(values: np.ndarray) -> np.ndarray:
    min_v = float(values.min()) if values.size else 0.0
    max_v = float(values.max()) if values.size else 0.0
    if max_v <= min_v:
        return np.zeros_like(values, dtype=float)
    return (values - min_v) / (max_v - min_v)


def _rank_labels_from_scores(scores: np.ndarray) -> list[str]:
    # Assignment context:
    # labels are simulated from historical performance ranking (not human-annotated labels).
    # This is acceptable here because the project uses seeded historical/mock data.
    order = np.argsort(-scores)  # high score first
    n = len(scores)
    top_cutoff = int(np.ceil(n / 3))
    mid_cutoff = int(np.ceil((2 * n) / 3))

    labels = ["Low Performer"] * n
    for rank, idx in enumerate(order):
        if rank < top_cutoff:
            labels[idx] = "Top Performer"
        elif rank < mid_cutoff:
            labels[idx] = "Average Performer"
        else:
            labels[idx] = "Low Performer"
    return labels


def _explanation_for_label(label: str) -> str:
    return (
        f"This product is classified as {label} because it has relatively "
        "high revenue, units sold, and order count compared with other products."
        if label == "Top Performer"
        else (
            f"This product is classified as {label} because its revenue, units sold, "
            "and order count are around the middle compared with other products."
            if label == "Average Performer"
            else f"This product is classified as {label} because its revenue, units sold, "
            "and order count are relatively lower compared with other products."
        )
    )


def get_ml_product_performance(db: Session) -> list[MLProductPerformanceItem]:
    # Dataset source: product_performance_view (existing reporting layer).
    rows = db.execute(
        text(
            """
            SELECT
                pp.product_id,
                pp.product_title,
                pp.product_category,
                pp.units_sold,
                pp.revenue,
                pp.orders_count,
                p.price
            FROM product_performance_view pp
            LEFT JOIN products p ON p.id = pp.product_id
            ORDER BY pp.product_id
            """
        )
    ).mappings().all()

    if not rows:
        return []

    # Preprocessing: numeric feature extraction with null-safe defaults.
    units = np.array([_to_float(row["units_sold"]) for row in rows], dtype=float)
    revenue = np.array([_to_float(row["revenue"]) for row in rows], dtype=float)
    orders = np.array([_to_float(row["orders_count"]) for row in rows], dtype=float)
    price = np.array([_to_float(row["price"]) for row in rows], dtype=float)

    # Simulated label generation from normalized historical performance score.
    score = (
        _safe_min_max_normalize(revenue)
        + _safe_min_max_normalize(units)
        + _safe_min_max_normalize(orders)
    )
    training_labels = _rank_labels_from_scores(score)

    # In-memory model training for assignment demo simplicity.
    # No persisted .pkl is used to keep architecture minimal.
    X = np.column_stack([units, revenue, orders, price])
    y = np.array(training_labels)

    model = DecisionTreeClassifier(max_depth=3, random_state=42)
    model.fit(X, y)

    predictions = model.predict(X)
    probabilities = model.predict_proba(X) if hasattr(model, "predict_proba") else None

    classes = list(model.classes_) if hasattr(model, "classes_") else []
    items: list[MLProductPerformanceItem] = []

    for idx, row in enumerate(rows):
        prediction = str(predictions[idx])
        confidence: float | None = None
        if probabilities is not None and classes:
            label_index = classes.index(prediction)
            confidence = float(probabilities[idx][label_index])

        items.append(
            MLProductPerformanceItem(
                product_id=_to_int(row["product_id"]),
                product_title=(row["product_title"] or "Unknown Product"),
                product_category=row["product_category"],
                units_sold=_to_int(row["units_sold"]),
                revenue=_to_float(row["revenue"]),
                orders_count=_to_int(row["orders_count"]),
                performance_class=prediction,
                confidence=confidence,
                explanation=_explanation_for_label(prediction),
            )
        )

    return items
