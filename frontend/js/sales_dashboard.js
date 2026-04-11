let salesTrendChart = null;
let isRefreshing = false;

function requireAuthToken() {
    if (typeof getToken !== "function") return true;
    const token = getToken();
    if (token) return true;
    window.location.href = "auth.html";
    return false;
}

function formatCurrency(value) {
    const number = Number(value || 0);
    return new Intl.NumberFormat(undefined, { style: "currency", currency: "USD" }).format(number);
}

function formatDateLabel(value) {
    if (!value) return "";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return "";
    return date.toLocaleDateString(undefined, { month: "short", day: "2-digit" });
}

function setText(id, value) {
    const el = document.getElementById(id);
    if (!el) return;
    el.textContent = value;
}

function showError(message) {
    const errorBox = document.getElementById("dashboardError");
    if (!errorBox) return;
    errorBox.textContent = message || "Failed to load analytics.";
    errorBox.classList.remove("hidden");
}

function hideError() {
    const errorBox = document.getElementById("dashboardError");
    if (!errorBox) return;
    errorBox.classList.add("hidden");
}

function setLoading(isLoading) {
    const loading = document.getElementById("dashboardLoading");
    const refreshBtn = document.getElementById("refreshAnalyticsBtn");
    if (!loading) return;
    if (isLoading) {
        loading.classList.remove("hidden");
    } else {
        loading.classList.add("hidden");
    }
    if (refreshBtn) {
        refreshBtn.disabled = isLoading;
        refreshBtn.classList.toggle("opacity-60", isLoading);
        refreshBtn.classList.toggle("cursor-not-allowed", isLoading);
    }
}

function setLastUpdatedNow() {
    const text = document.getElementById("lastUpdatedText");
    if (!text) return;
    const now = new Date();
    text.textContent = `Last updated: ${now.toLocaleString()}`;
}

function validateSalesSummary(summary) {
    if (!summary || typeof summary !== "object") return false;
    const required = [
        "total_revenue",
        "completed_orders",
        "pending_orders",
        "failed_orders",
        "avg_order_value",
        "total_units_sold",
    ];
    return required.every((key) => Number.isFinite(Number(summary[key])));
}

function normalizeTrendItems(items) {
    const source = Array.isArray(items) ? items : [];
    return source
        .filter((row) =>
            row &&
            row.order_date &&
            Number.isFinite(Number(row.orders_count)) &&
            Number.isFinite(Number(row.units_sold)) &&
            Number.isFinite(Number(row.revenue))
        )
        .map((row) => ({
            order_date: row.order_date,
            orders_count: Math.max(0, Number(row.orders_count)),
            units_sold: Math.max(0, Number(row.units_sold)),
            revenue: Math.max(0, Number(row.revenue)),
        }));
}

function renderSummary(summary) {
    setText("kpiTotalRevenue", formatCurrency(summary.total_revenue));
    setText("kpiCompletedOrders", String(summary.completed_orders ?? 0));
    setText("kpiPendingOrders", String(summary.pending_orders ?? 0));
    setText("kpiFailedOrders", String(summary.failed_orders ?? 0));
    setText("kpiAvgOrderValue", formatCurrency(summary.avg_order_value));
    setText("kpiTotalUnitsSold", String(summary.total_units_sold ?? 0));

    const section = document.getElementById("kpiSection");
    if (section) section.classList.remove("hidden");
}

function renderTrend(items) {
    const safeItems = Array.isArray(items) ? items : [];
    const section = document.getElementById("trendSection");
    const emptyState = document.getElementById("trendEmptyState");
    const chartWrap = document.getElementById("trendChartWrap");
    const canvas = document.getElementById("salesTrendChart");

    if (section) section.classList.remove("hidden");

    if (!safeItems.length) {
        if (emptyState) emptyState.classList.remove("hidden");
        if (chartWrap) chartWrap.classList.add("hidden");
        return;
    }

    if (emptyState) emptyState.classList.add("hidden");
    if (chartWrap) chartWrap.classList.remove("hidden");

    const labels = safeItems.map((row) => formatDateLabel(row.order_date));
    const revenueSeries = safeItems.map((row) => Number(row.revenue || 0));
    const orderSeries = safeItems.map((row) => Number(row.orders_count || 0));

    if (salesTrendChart) {
        salesTrendChart.destroy();
    }

    salesTrendChart = new Chart(canvas, {
        type: "line",
        data: {
            labels,
            datasets: [
                {
                    label: "Revenue",
                    data: revenueSeries,
                    borderColor: "#84b214",
                    backgroundColor: "rgba(132, 178, 20, 0.2)",
                    yAxisID: "yRevenue",
                    tension: 0.25,
                    fill: true,
                },
                {
                    label: "Orders",
                    data: orderSeries,
                    borderColor: "#2563eb",
                    backgroundColor: "rgba(37, 99, 235, 0.15)",
                    yAxisID: "yOrders",
                    tension: 0.2,
                    fill: false,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: "index", intersect: false },
            plugins: {
                legend: { position: "top" },
            },
            scales: {
                yRevenue: {
                    type: "linear",
                    position: "left",
                    ticks: {
                        callback: (value) => `$${value}`,
                    },
                },
                yOrders: {
                    type: "linear",
                    position: "right",
                    grid: { drawOnChartArea: false },
                },
            },
        },
    });
}

async function updateHealthBadge() {
    const healthBadge = document.getElementById("healthBadge");
    const healthIcon = document.getElementById("healthIcon");
    if (!healthBadge || !healthIcon) return;

    try {
        const apiHost = typeof API_BASE !== "undefined" ? API_BASE : "http://localhost:8000";
        const response = await fetch(`${apiHost}/health`, { method: "GET" });
        if (response.ok) {
            healthIcon.textContent = "cloud_done";
            healthIcon.className = "material-symbols-outlined text-green-500";
            healthBadge.title = "System Online: All Services Operational";
            return;
        }
        healthIcon.textContent = "cloud_off";
        healthIcon.className = "material-symbols-outlined text-yellow-500";
        healthBadge.title = "System Degraded";
    } catch (err) {
        healthIcon.textContent = "cloud_off";
        healthIcon.className = "material-symbols-outlined text-red-500";
        healthBadge.title = "System Offline: Backend API Unreachable";
    }
}

async function loadSalesDashboard() {
    if (isRefreshing) return;
    isRefreshing = true;
    setLoading(true);
    hideError();

    try {
        const [summary, trend] = await Promise.all([
            apiRequest("/api/analytics/sales/summary", "GET", null, true),
            apiRequest("/api/analytics/sales/trend", "GET", null, true),
        ]);

        if (!summary || !trend) return;
        if (!validateSalesSummary(summary)) {
            throw new Error("Invalid sales summary response");
        }
        const trendItems = normalizeTrendItems(trend.items);

        renderSummary(summary);
        renderTrend(trendItems);
        setLastUpdatedNow();
    } catch (error) {
        showError(error?.message || "Analytics service is unavailable.");
    } finally {
        setLoading(false);
        isRefreshing = false;
    }
}

document.addEventListener("DOMContentLoaded", async () => {
    if (!requireAuthToken()) return;
    const refreshBtn = document.getElementById("refreshAnalyticsBtn");
    if (refreshBtn) {
        refreshBtn.addEventListener("click", () => {
            loadSalesDashboard();
        });
    }
    await updateHealthBadge();
    await loadSalesDashboard();
});
