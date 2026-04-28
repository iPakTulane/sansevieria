let topProductsChart = null;
let isRefreshing = false;
let allSemanticItems = [];

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

function formatNumber(value) {
    return new Intl.NumberFormat().format(Number(value || 0));
}

function showError(message) {
    const errorBox = document.getElementById("dashboardError");
    if (!errorBox) return;
    errorBox.textContent = message || "Failed to load product analytics.";
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

function normalizeProductItems(items) {
    const source = Array.isArray(items) ? items : [];
    // Defensive normalization prevents broken cards/tables if payload is partial.
    return source
        .filter((item) =>
            item &&
            Number.isFinite(Number(item.product_id)) &&
            Number.isFinite(Number(item.units_sold)) &&
            Number.isFinite(Number(item.revenue)) &&
            Number.isFinite(Number(item.orders_count))
        )
        .map((item) => ({
            product_id: Number(item.product_id),
            product_title: item.product_title || "Unknown Product",
            product_category: item.product_category || "Uncategorized",
            units_sold: Math.max(0, Number(item.units_sold)),
            revenue: Math.max(0, Number(item.revenue)),
            orders_count: Math.max(0, Number(item.orders_count)),
            performance_class: (item.performance_class || "N/A").trim(),
            confidence: Number.isFinite(Number(item.confidence)) ? Number(item.confidence) : null,
            semantic_explanation: item.semantic_explanation || item.explanation || "No semantic explanation available.",
            semantic_triples: Array.isArray(item.semantic_triples) ? item.semantic_triples : [],
        }));
}

function getPerformanceBadgeClass(performanceClass) {
    if (performanceClass === "Top Performer") {
        return "bg-green-100 text-green-700 border border-green-200";
    }
    if (performanceClass === "Average Performer") {
        return "bg-slate-100 text-slate-700 border border-slate-200";
    }
    if (performanceClass === "Low Performer") {
        return "bg-amber-100 text-amber-700 border border-amber-200";
    }
    return "bg-slate-100 text-slate-600 border border-slate-200";
}

function formatConfidence(value) {
    if (!Number.isFinite(Number(value))) return "N/A";
    return `${Math.round(Number(value) * 100)}%`;
}

function renderRankList(targetId, items) {
    const container = document.getElementById(targetId);
    if (!container) return;
    container.innerHTML = "";

    items.forEach((item, idx) => {
        const row = document.createElement("div");
        row.className = "flex items-center justify-between rounded-lg border border-slate-200 dark:border-slate-700 px-3 py-2";
        row.innerHTML = `
            <div class="min-w-0">
                <p class="text-xs text-slate-500">#${idx + 1}</p>
                <p class="text-sm font-semibold truncate">${item.product_title || "Unknown Product"}</p>
                <p class="text-xs text-slate-500">${item.product_category || "Uncategorized"}</p>
            </div>
            <div class="text-right">
                <p class="text-xs mb-1">
                    <span class="inline-flex items-center rounded-full px-2 py-0.5 font-semibold ${getPerformanceBadgeClass(item.performance_class)}">
                        ${item.performance_class || "N/A"}
                    </span>
                </p>
                <p class="text-sm font-bold">${formatCurrency(item.revenue)}</p>
                <p class="text-xs text-slate-500">${formatNumber(item.units_sold)} units</p>
            </div>
        `;
        container.appendChild(row);
    });
}

function renderTable(items) {
    const section = document.getElementById("tableSection");
    const tableWrap = document.getElementById("tableWrap");
    const emptyState = document.getElementById("tableEmptyState");
    const tbody = document.getElementById("performanceTableBody");

    if (section) section.classList.remove("hidden");
    if (!tbody) return;

    tbody.innerHTML = "";
    if (!items.length) {
        if (tableWrap) tableWrap.classList.add("hidden");
        if (emptyState) emptyState.classList.remove("hidden");
        return;
    }

    if (tableWrap) tableWrap.classList.remove("hidden");
    if (emptyState) emptyState.classList.add("hidden");

    items.forEach((item) => {
        const tr = document.createElement("tr");
        tr.className = "hover:bg-background-light dark:hover:bg-slate-800/50 transition-colors";
        const triplesText = item.semantic_triples
            .slice(0, 6)
            .map((t) => `${t.subject} -> ${t.predicate} -> ${t.object}`)
            .join("\n");
        tr.innerHTML = `
            <td class="py-3 text-sm font-medium">${item.product_title || "—"}</td>
            <td class="py-3 text-sm text-slate-500">${item.product_category || "Uncategorized"}</td>
            <td class="py-3 text-sm text-right">${formatNumber(item.units_sold)}</td>
            <td class="py-3 text-sm text-right">${formatNumber(item.orders_count)}</td>
            <td class="py-3 text-sm text-right font-semibold">${formatCurrency(item.revenue)}</td>
            <td class="py-3 text-sm">
                <span class="inline-flex items-center rounded-full px-2 py-1 text-xs font-semibold ${getPerformanceBadgeClass(item.performance_class)}">
                    ${item.performance_class || "N/A"}
                </span>
            </td>
            <td class="py-3 text-sm text-right">${formatConfidence(item.confidence)}</td>
            <td class="py-3 text-xs text-slate-600 dark:text-slate-300 max-w-[380px]">
                <p>${item.semantic_explanation || "No semantic explanation available."}</p>
                ${triplesText ? `
                <details class="mt-2">
                    <summary class="cursor-pointer text-primary font-semibold">View Triples</summary>
                    <pre class="mt-1 whitespace-pre-wrap text-[11px] leading-5 text-slate-500 dark:text-slate-400">${triplesText}</pre>
                </details>` : ""}
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function applyClassFilterAndRender() {
    const filterEl = document.getElementById("performanceClassFilter");
    const selected = filterEl ? filterEl.value : "All";
    const items = selected === "All"
        ? [...allSemanticItems]
        : allSemanticItems.filter((item) => item.performance_class === selected);
    renderTable(items);
}

function renderTopChart(items) {
    const section = document.getElementById("chartSection");
    const chartWrap = document.getElementById("chartWrap");
    const emptyState = document.getElementById("chartEmptyState");
    const canvas = document.getElementById("topProductsChart");

    if (section) section.classList.remove("hidden");

    if (!items.length) {
        if (chartWrap) chartWrap.classList.add("hidden");
        if (emptyState) emptyState.classList.remove("hidden");
        return;
    }

    if (chartWrap) chartWrap.classList.remove("hidden");
    if (emptyState) emptyState.classList.add("hidden");

    const chartItems = items.slice(0, 8);
    const labels = chartItems.map((p) => p.product_title || `Product ${p.product_id}`);
    const revenues = chartItems.map((p) => Number(p.revenue || 0));

    if (topProductsChart) {
        topProductsChart.destroy();
    }

    topProductsChart = new Chart(canvas, {
        type: "bar",
        data: {
            labels,
            datasets: [
                {
                    label: "Revenue",
                    data: revenues,
                    backgroundColor: "rgba(132, 178, 20, 0.75)",
                    borderColor: "#84b214",
                    borderWidth: 1,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { callback: (value) => `$${value}` },
                },
                x: {
                    ticks: { maxRotation: 45, minRotation: 20 },
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

async function loadProductDashboard() {
    if (isRefreshing) return;
    isRefreshing = true;
    setLoading(true);
    hideError();

    try {
        // Product dashboard uses ML + semantic endpoint for Assignment 5 integration.
        const response = await apiRequest("/api/analytics/products/performance-semantic", "GET", null, true);
        if (!response) return;

        const items = normalizeProductItems(response.items);
        items.sort((a, b) => Number(b.revenue || 0) - Number(a.revenue || 0));
        allSemanticItems = items;

        const section = document.getElementById("topBottomSection");
        if (section) section.classList.remove("hidden");

        const top = items.slice(0, 5);
        const bottom = items.slice().sort((a, b) => Number(a.revenue || 0) - Number(b.revenue || 0)).slice(0, 5);

        renderRankList("topProductsList", top);
        renderRankList("bottomProductsList", bottom);
        renderTopChart(items);
        applyClassFilterAndRender();
        setLastUpdatedNow();
    } catch (error) {
        showError(error?.message || "Product semantic analytics service is unavailable.");
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
            // Explicit refresh makes live-demo behavior predictable for reviewers.
            loadProductDashboard();
        });
    }
    const classFilter = document.getElementById("performanceClassFilter");
    if (classFilter) {
        classFilter.addEventListener("change", applyClassFilterAndRender);
    }
    await updateHealthBadge();
    await loadProductDashboard();
});
