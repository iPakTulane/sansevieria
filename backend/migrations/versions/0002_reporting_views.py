"""reporting views for analytics

Revision ID: 0002
Revises: 0001
Create Date: 2026-04-11 01:30:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "0002"
down_revision: Union[str, Sequence[str], None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Line-level sales fact view for flexible BI slicing.
    op.execute(
        """
        CREATE VIEW sales_order_items_fact_view AS
        SELECT
            o.id AS order_pk,
            o.order_id,
            o.user_id,
            u.email AS user_email,
            o.status AS order_status,
            o.created_at AS order_created_at,
            DATE(o.created_at) AS order_date,
            o.total_amount AS order_total_amount,
            oi.id AS order_item_id,
            oi.product_id,
            p.title AS product_title,
            p.category AS product_category,
            oi.quantity,
            oi.price_at_purchase AS unit_price_at_purchase,
            (oi.quantity * oi.price_at_purchase) AS line_total_amount
        FROM orders o
        JOIN order_items oi ON oi.order_id = o.id
        JOIN products p ON p.id = oi.product_id
        LEFT JOIN users u ON u.id = o.user_id;
        """
    )

    # Sales KPI summary: single-row snapshot for headline cards.
    op.execute(
        """
        CREATE VIEW sales_summary_view AS
        SELECT
            COALESCE(SUM(CASE WHEN status = 'COMPLETED' THEN total_amount ELSE 0 END), 0) AS total_revenue,
            SUM(CASE WHEN status = 'COMPLETED' THEN 1 ELSE 0 END) AS completed_orders,
            SUM(CASE WHEN status = 'PENDING' THEN 1 ELSE 0 END) AS pending_orders,
            SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) AS failed_orders,
            COALESCE(AVG(CASE WHEN status = 'COMPLETED' THEN total_amount END), 0) AS avg_order_value,
            COALESCE(
                (
                    SELECT SUM(oi.quantity)
                    FROM order_items oi
                    JOIN orders o2 ON o2.id = oi.order_id
                    WHERE o2.status = 'COMPLETED'
                ),
                0
            ) AS total_units_sold,
            MIN(CASE WHEN status = 'COMPLETED' THEN created_at END) AS first_completed_order_at,
            MAX(CASE WHEN status = 'COMPLETED' THEN created_at END) AS last_completed_order_at
        FROM orders;
        """
    )

    # Daily sales trend (for time-series visuals).
    op.execute(
        """
        CREATE VIEW sales_over_time_view AS
        SELECT
            order_date,
            COUNT(DISTINCT order_pk) AS orders_count,
            COALESCE(SUM(quantity), 0) AS units_sold,
            COALESCE(SUM(line_total_amount), 0) AS revenue
        FROM sales_order_items_fact_view
        WHERE order_status = 'COMPLETED'
        GROUP BY order_date
        ORDER BY order_date;
        """
    )

    # Product performance (supports top/bottom seller analysis).
    op.execute(
        """
        CREATE VIEW product_performance_view AS
        SELECT
            p.id AS product_id,
            p.title AS product_title,
            p.category AS product_category,
            COALESCE(SUM(f.quantity), 0) AS units_sold,
            COALESCE(SUM(f.line_total_amount), 0) AS revenue,
            COUNT(DISTINCT f.order_pk) AS orders_count
        FROM products p
        LEFT JOIN sales_order_items_fact_view f
            ON f.product_id = p.id
            AND f.order_status = 'COMPLETED'
        GROUP BY p.id, p.title, p.category
        ORDER BY revenue DESC, units_sold DESC, p.id;
        """
    )


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS product_performance_view;")
    op.execute("DROP VIEW IF EXISTS sales_over_time_view;")
    op.execute("DROP VIEW IF EXISTS sales_summary_view;")
    op.execute("DROP VIEW IF EXISTS sales_order_items_fact_view;")
