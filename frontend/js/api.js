const API_BASE = "http://localhost:8000";

function getToken() {
    return localStorage.getItem("access_token");
}

function setToken(token) {
    localStorage.setItem("access_token", token);
}

function clearToken() {
    localStorage.removeItem("access_token");
}

async function apiRequest(endpoint, method = "GET", data = null, auth = false) {
    const url = `${API_BASE}${endpoint}`;
    const headers = {
        "Content-Type": "application/json"
    };

    if (auth) {
        const token = getToken();
        if (token) {
            headers["Authorization"] = `Bearer ${token}`;
        }
    }

    const options = {
        method,
        headers
    };

    if (data && method !== "GET" && method !== "HEAD") {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(url, options);

        if (response.status === 401) {
            clearToken();
            window.location.href = "auth.html";
            return null;
        }

        if (!response.ok) {
            let errorMessage = `HTTP error! status: ${response.status}`;
            try {
                const errorData = await response.json();
                if (errorData.detail) errorMessage = errorData.detail;
            } catch (e) {
                // Ignore JSON parse error for non-JSON responses
            }
            throw new Error(errorMessage);
        }

        return await response.json();
    } catch (error) {
        console.error("[Sansevieria API Error]", error);
        alert(error.message || "An error occurred connecting to the server.");
        throw error;
    }
}
