(function () {
    const apiHost = (typeof API_BASE !== "undefined") ? API_BASE : "http://localhost:8000";
    const chatEndpoint = `${apiHost}/api/chat/`;

    const CHAT_SESSIONS_KEY = "sansevieria_chat_sessions_v1";
    const CHAT_ACTIVE_SESSION_KEY = "sansevieria_chat_active_session_v1";

    const messagesEl = document.getElementById("chatMessages");
    const inputEl = document.getElementById("chatInput");
    const sendBtn = document.getElementById("sendMessageBtn");
    const clearBtn = document.getElementById("clearChatBtn");
    const exportBtn = document.getElementById("exportLogsBtn");
    const greetingEl = document.getElementById("chatGreeting");
    const readinessBannerEl = document.getElementById("chatReadinessBanner");
    const sessionsListEl = document.getElementById("chatSessionsList");
    const newChatBtn = document.getElementById("newChatBtn");

    if (!messagesEl || !inputEl || !sendBtn || !clearBtn || !exportBtn || !sessionsListEl || !newChatBtn) {
        return;
    }

    const initialGreetingHTML = greetingEl ? greetingEl.outerHTML : "";

    const chatLog = [];
    const conversationHistory = [];
    const MEMORY_LIMIT = 8; // Last 8 role messages (~4 user/assistant exchanges).

    let sessions = [];
    let activeSessionId = null;

    let isSending = false;
    let activeRequestController = null;
    let renderGeneration = 0;

    function nowIso() {
        return new Date().toISOString();
    }

    function generateSessionId() {
        return `chat_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
    }

    function getAccessToken() {
        return localStorage.getItem("access_token");
    }

    function scrollToBottom() {
        messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    function escapeHtml(text) {
        return String(text)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/\"/g, "&quot;")
            .replace(/'/g, "&#39;");
    }

    function renderMarkdown(text) {
        const value = String(text || "");

        if (!value.trim()) {
            return "";
        }

        try {
            if (typeof marked !== "undefined" && marked && typeof marked.parse === "function") {
                const rawHtml = marked.parse(value, { breaks: true });
                if (typeof DOMPurify !== "undefined" && DOMPurify && typeof DOMPurify.sanitize === "function") {
                    return DOMPurify.sanitize(rawHtml);
                }
                return rawHtml;
            }
        } catch (_err) {
            // Fall through to escaped plain-text fallback.
        }

        return escapeHtml(value).replace(/\n/g, "<br>");
    }

    function truncate(text, max = 56) {
        const value = String(text || "").trim();
        if (!value) return "";
        if (value.length <= max) return value;
        return `${value.slice(0, max - 1)}…`;
    }

    function formatSessionTime(isoString) {
        if (!isoString) return "";
        const dt = new Date(isoString);
        if (Number.isNaN(dt.getTime())) return "";
        return dt.toLocaleString(undefined, {
            month: "short",
            day: "2-digit",
            hour: "2-digit",
            minute: "2-digit",
        });
    }

    function buildUserMessageHtml(text) {
        return `
            <div class="flex flex-row-reverse items-start gap-3 chat-dynamic-message" data-role="user">
                <div class="w-9 h-9 rounded-lg bg-slate-200 dark:bg-slate-700 flex items-center justify-center shrink-0">
                    <span class="material-symbols-outlined text-slate-500 dark:text-slate-400 text-lg">person</span>
                </div>
                <div class="flex flex-col gap-1 max-w-[78%] items-end">
                    <p class="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">You</p>
                    <div class="inline-block w-fit max-w-full bg-primary text-slate-900 px-3 py-1.5 rounded-xl rounded-tr-none font-medium break-words whitespace-pre-line leading-snug">${escapeHtml(text)}</div>
                </div>
            </div>
        `;
    }

    function buildAssistantMessageHtml(text, metaText) {
        const renderedMessage = renderMarkdown(text);
        return `
            <div class="flex items-start gap-3 chat-dynamic-message" data-role="assistant">
                <div class="w-9 h-9 rounded-lg bg-primary flex items-center justify-center shrink-0">
                    <span class="material-symbols-outlined text-white text-lg">psychology</span>
                </div>
                <div class="flex flex-col gap-1 max-w-[78%]">
                    <p class="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">Sansevieria AI</p>
                    <div class="chat-message-content inline-block w-fit max-w-full bg-primary/10 dark:bg-primary/5 text-left indent-0 text-slate-800 dark:text-slate-200 px-3 py-1.5 rounded-xl rounded-tl-none border border-primary/10 break-words leading-snug">${renderedMessage}</div>
                    ${metaText ? `<p class="text-[10px] text-slate-400">${escapeHtml(metaText)}</p>` : ""}
                </div>
            </div>
        `;
    }

    function appendMessage(role, text, metaText) {
        const wrapper = document.createElement("div");
        wrapper.innerHTML = role === "user" ? buildUserMessageHtml(text) : buildAssistantMessageHtml(text, metaText);
        const node = wrapper.firstElementChild;
        if (node) {
            messagesEl.appendChild(node);
            scrollToBottom();
        }
    }

    function showReadinessBanner(level, text) {
        if (!readinessBannerEl) return;
        readinessBannerEl.classList.remove("hidden");
        readinessBannerEl.className = "rounded-lg border px-4 py-2 text-xs font-medium";
        if (level === "ok") {
            readinessBannerEl.classList.add("border-green-200", "bg-green-50", "text-green-700");
        } else if (level === "degraded") {
            readinessBannerEl.classList.add("border-amber-200", "bg-amber-50", "text-amber-700");
        } else {
            readinessBannerEl.classList.add("border-red-200", "bg-red-50", "text-red-700");
        }
        readinessBannerEl.textContent = text;
    }

    async function loadChatReadiness() {
        const token = getAccessToken();
        if (!token) {
            showReadinessBanner("degraded", "Sign in to use the AI plant assistant.");
            return;
        }

        try {
            const response = await fetch(`${chatEndpoint}health`, {
                method: "GET",
                headers: {
                    "Authorization": `Bearer ${token}`,
                },
            });

            if (response.status === 401) {
                localStorage.removeItem("access_token");
                showReadinessBanner("degraded", "Session expired. Please sign in to use the AI assistant.");
                return;
            }

            let payload = null;
            try {
                payload = await response.json();
            } catch (_err) {
                payload = null;
            }

            if (!response.ok || !payload) {
                showReadinessBanner("unavailable", "AI assistant status is unavailable right now.");
                return;
            }

            const status = payload.status === "ok" ? "ok" : payload.status === "degraded" ? "degraded" : "unavailable";
            const message = payload.message || "AI assistant status is currently unknown.";
            showReadinessBanner(status, message);
        } catch (_err) {
            showReadinessBanner("unavailable", "AI assistant is currently unavailable. Make sure LM Studio is running and a model is loaded.");
        }
    }

    function removeStaticSamples() {
        messagesEl.querySelectorAll('[data-static-chat="sample"]').forEach((el) => el.remove());
    }

    function removeGreetingIfNeeded() {
        const currentGreeting = document.getElementById("chatGreeting");
        if (currentGreeting && currentGreeting.parentElement) {
            currentGreeting.remove();
        }
    }

    function ensureGreetingIfEmpty() {
        if (chatLog.length > 0) return;
        if (messagesEl.querySelector("#chatGreeting")) return;
        if (!initialGreetingHTML) return;

        const wrap = document.createElement("div");
        wrap.innerHTML = initialGreetingHTML;
        const greetingNode = wrap.firstElementChild;
        if (greetingNode) {
            messagesEl.appendChild(greetingNode);
        }
    }

    function setSendingState(sending) {
        isSending = sending;
        sendBtn.disabled = sending;
        inputEl.disabled = sending;
        sendBtn.classList.toggle("opacity-60", sending);
        sendBtn.classList.toggle("cursor-not-allowed", sending);
    }

    function addThinkingBubble() {
        const wrapper = document.createElement("div");
        wrapper.innerHTML = buildAssistantMessageHtml("Thinking...", "Waiting for local model response");
        const node = wrapper.firstElementChild;
        if (node) {
            node.id = "chatThinkingBubble";
            messagesEl.appendChild(node);
            scrollToBottom();
        }
    }

    function removeThinkingBubble() {
        const thinking = document.getElementById("chatThinkingBubble");
        if (thinking) {
            thinking.remove();
        }
    }

    function sleep(ms) {
        return new Promise((resolve) => setTimeout(resolve, ms));
    }

    function createAssistantMessageNode(initialText, metaText) {
        const wrapper = document.createElement("div");
        wrapper.innerHTML = buildAssistantMessageHtml(initialText, metaText);
        return wrapper.firstElementChild;
    }

    async function renderAssistantProgressively(fullText, metaText, generationAtStart) {
        const node = createAssistantMessageNode("", metaText);
        if (!node) return false;

        const contentEl = node.querySelector(".chat-message-content");
        if (!contentEl) return false;

        messagesEl.appendChild(node);
        scrollToBottom();

        const text = String(fullText || "");
        const total = text.length;
        if (!total) {
            contentEl.textContent = "";
            return true;
        }

        const chunkSize = total > 500 ? 6 : total > 220 ? 4 : 2;
        const delayMs = 12;
        let index = 0;

        while (index < total) {
            if (generationAtStart !== renderGeneration) {
                return false;
            }
            index = Math.min(total, index + chunkSize);
            contentEl.textContent = `${text.slice(0, index)}▍`;
            scrollToBottom();
            await sleep(delayMs);
        }

        if (generationAtStart !== renderGeneration) {
            return false;
        }

        contentEl.innerHTML = renderMarkdown(text);
        scrollToBottom();
        return true;
    }

    function trimConversationHistory() {
        if (conversationHistory.length > MEMORY_LIMIT) {
            const trimmed = conversationHistory.slice(-MEMORY_LIMIT);
            conversationHistory.length = 0;
            conversationHistory.push(...trimmed);
        }
    }

    function cloneSimpleArray(target, source) {
        target.length = 0;
        source.forEach((item) => target.push(item));
    }

    function normalizeSession(raw) {
        if (!raw || typeof raw !== "object") return null;
        if (!raw.id || typeof raw.id !== "string") return null;

        const createdAt = typeof raw.createdAt === "string" ? raw.createdAt : nowIso();
        const updatedAt = typeof raw.updatedAt === "string" ? raw.updatedAt : createdAt;

        const safeChatLog = Array.isArray(raw.chatLog)
            ? raw.chatLog.filter((m) => m && (m.role === "user" || m.role === "assistant") && typeof m.content === "string")
            : [];

        const safeConversation = Array.isArray(raw.conversationHistory)
            ? raw.conversationHistory.filter((m) => m && (m.role === "user" || m.role === "assistant") && typeof m.content === "string")
            : [];

        return {
            id: raw.id,
            title: typeof raw.title === "string" && raw.title.trim() ? raw.title.trim() : "New chat",
            preview: typeof raw.preview === "string" ? raw.preview : "",
            createdAt,
            updatedAt,
            chatLog: safeChatLog,
            conversationHistory: safeConversation,
        };
    }

    function loadStoredSessions() {
        try {
            const raw = localStorage.getItem(CHAT_SESSIONS_KEY);
            if (!raw) return [];
            const parsed = JSON.parse(raw);
            if (!Array.isArray(parsed)) return [];
            return parsed.map(normalizeSession).filter(Boolean);
        } catch (_err) {
            return [];
        }
    }

    function saveStoredSessions() {
        localStorage.setItem(CHAT_SESSIONS_KEY, JSON.stringify(sessions));
    }

    function loadStoredActiveSessionId() {
        return localStorage.getItem(CHAT_ACTIVE_SESSION_KEY);
    }

    function saveStoredActiveSessionId() {
        if (activeSessionId) {
            localStorage.setItem(CHAT_ACTIVE_SESSION_KEY, activeSessionId);
        }
    }

    function createEmptySession() {
        const ts = nowIso();
        return {
            id: generateSessionId(),
            title: "New chat",
            preview: "No messages yet",
            createdAt: ts,
            updatedAt: ts,
            chatLog: [],
            conversationHistory: [],
        };
    }

    function getActiveSession() {
        return sessions.find((s) => s.id === activeSessionId) || null;
    }

    function deriveSessionTitle(logItems) {
        const firstUser = logItems.find((m) => m.role === "user" && typeof m.content === "string" && m.content.trim());
        if (!firstUser) return "New chat";
        return truncate(firstUser.content, 42);
    }

    function deriveSessionPreview(logItems) {
        if (!logItems.length) return "No messages yet";
        const last = logItems[logItems.length - 1];
        const prefix = last.role === "assistant" ? "AI: " : "You: ";
        return `${prefix}${truncate(last.content, 52)}`;
    }

    function persistActiveSessionFromMemory(options = {}) {
        const { touchUpdatedAt = true } = options;
        const active = getActiveSession();
        if (!active) return;

        active.chatLog = chatLog.map((m) => ({ ...m }));
        active.conversationHistory = conversationHistory.map((m) => ({ ...m }));
        active.title = deriveSessionTitle(active.chatLog);
        active.preview = deriveSessionPreview(active.chatLog);
        if (touchUpdatedAt) {
            active.updatedAt = nowIso();
        }

        saveStoredSessions();
        renderSessionsSidebar();
    }

    function hydrateMemoryFromActiveSession() {
        const active = getActiveSession();
        if (!active) {
            cloneSimpleArray(chatLog, []);
            cloneSimpleArray(conversationHistory, []);
            return;
        }

        cloneSimpleArray(chatLog, active.chatLog.map((m) => ({ ...m })));
        cloneSimpleArray(conversationHistory, active.conversationHistory.map((m) => ({ ...m })));
        trimConversationHistory();
    }

    function stopCurrentInteraction() {
        renderGeneration += 1;
        if (activeRequestController) {
            activeRequestController.abort();
            activeRequestController = null;
        }
        removeThinkingBubble();
        setSendingState(false);
    }

    function renderThreadFromMemory() {
        stopCurrentInteraction();

        messagesEl.querySelectorAll(".chat-dynamic-message").forEach((el) => el.remove());
        removeStaticSamples();

        if (chatLog.length > 0) {
            removeGreetingIfNeeded();
            chatLog.forEach((item) => {
                if (item.role === "user") {
                    appendMessage("user", item.content);
                    return;
                }
                const provider = item.provider ? String(item.provider) : "";
                const model = item.model ? String(item.model) : "";
                const meta = model ? `${provider} • ${model}` : provider;
                appendMessage("assistant", item.content, meta || undefined);
            });
        } else {
            ensureGreetingIfEmpty();
        }

        scrollToBottom();
    }

    function renderSessionsSidebar() {
        sessionsListEl.innerHTML = "";

        const ordered = [...sessions].sort((a, b) => {
            const aTime = new Date(a.createdAt).getTime() || 0;
            const bTime = new Date(b.createdAt).getTime() || 0;
            return bTime - aTime;
        });

        if (!ordered.length) {
            const empty = document.createElement("div");
            empty.className = "rounded-lg border border-primary/10 bg-white dark:bg-slate-900/60 px-3 py-2 text-xs text-slate-500";
            empty.textContent = "No chats yet.";
            sessionsListEl.appendChild(empty);
            return;
        }

        ordered.forEach((session) => {
            const btn = document.createElement("button");
            const isActive = session.id === activeSessionId;
            btn.type = "button";
            btn.className = isActive
                ? "w-full text-left rounded-lg border border-primary/40 bg-primary/10 px-3 py-2 transition-colors"
                : "w-full text-left rounded-lg border border-primary/10 bg-white dark:bg-slate-900/60 px-3 py-2 hover:bg-primary/5 transition-colors";

            btn.innerHTML = `
                <p class="text-xs font-semibold text-slate-800 dark:text-slate-100 truncate">${escapeHtml(session.title || "New chat")}</p>
                <p class="mt-1 text-[11px] text-slate-500 truncate">${escapeHtml(session.preview || "No messages yet")}</p>
                <p class="mt-1 text-[10px] text-slate-400">${escapeHtml(formatSessionTime(session.updatedAt))}</p>
            `;

            btn.addEventListener("click", () => {
                if (session.id === activeSessionId) return;
                persistActiveSessionFromMemory({ touchUpdatedAt: false });
                activeSessionId = session.id;
                saveStoredActiveSessionId();
                hydrateMemoryFromActiveSession();
                renderSessionsSidebar();
                renderThreadFromMemory();
            });

            sessionsListEl.appendChild(btn);
        });
    }

    function ensureSessionState() {
        sessions = loadStoredSessions();
        activeSessionId = loadStoredActiveSessionId();

        if (!sessions.length) {
            const first = createEmptySession();
            sessions.push(first);
            activeSessionId = first.id;
            saveStoredSessions();
            saveStoredActiveSessionId();
        }

        if (!sessions.find((s) => s.id === activeSessionId)) {
            sessions.sort((a, b) => (new Date(b.createdAt).getTime() || 0) - (new Date(a.createdAt).getTime() || 0));
            activeSessionId = sessions[0].id;
            saveStoredActiveSessionId();
        }

        hydrateMemoryFromActiveSession();
    }

    function startNewChat() {
        persistActiveSessionFromMemory({ touchUpdatedAt: false });
        const fresh = createEmptySession();
        sessions.unshift(fresh);
        activeSessionId = fresh.id;
        saveStoredSessions();
        saveStoredActiveSessionId();
        hydrateMemoryFromActiveSession();
        renderSessionsSidebar();
        renderThreadFromMemory();
        inputEl.focus();
    }

    async function sendMessage() {
        if (isSending) return;
        const generationAtStart = renderGeneration;

        const message = inputEl.value.trim();
        if (!message) return;

        removeGreetingIfNeeded();
        removeStaticSamples();
        appendMessage("user", message);

        chatLog.push({
            role: "user",
            content: message,
            timestamp: nowIso(),
        });
        conversationHistory.push({
            role: "user",
            content: message,
        });
        trimConversationHistory();
        persistActiveSessionFromMemory();

        inputEl.value = "";
        setSendingState(true);
        addThinkingBubble();
        const requestController = new AbortController();
        activeRequestController = requestController;

        try {
            const requestMessages = [...conversationHistory.slice(-MEMORY_LIMIT)];
            const token = getAccessToken();
            if (!token) {
                throw new Error("Please sign in to use the plant assistant.");
            }

            const response = await fetch(chatEndpoint, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`,
                },
                body: JSON.stringify({ messages: requestMessages }),
                signal: requestController.signal,
            });

            if (response.status === 401) {
                localStorage.removeItem("access_token");
                throw new Error("Your session expired. Please sign in again.");
            }

            let payload = null;
            try {
                payload = await response.json();
            } catch (_err) {
                payload = null;
            }

            if (!response.ok) {
                const detail = payload && payload.detail ? String(payload.detail) : "Chat service is unavailable right now.";
                throw new Error(detail);
            }

            const assistantText = payload && typeof payload.response === "string" ? payload.response.trim() : "";
            if (!assistantText) {
                throw new Error("The assistant returned an empty response.");
            }

            const provider = payload && payload.provider ? String(payload.provider) : "unknown";
            const model = payload && payload.model ? String(payload.model) : "";
            const meta = model ? `${provider} • ${model}` : provider;

            removeThinkingBubble();
            const renderCompleted = await renderAssistantProgressively(assistantText, meta, generationAtStart);
            if (!renderCompleted) {
                return;
            }

            chatLog.push({
                role: "assistant",
                content: assistantText,
                provider,
                model: model || null,
                timestamp: nowIso(),
            });
            conversationHistory.push({
                role: "assistant",
                content: assistantText,
            });
            trimConversationHistory();
            persistActiveSessionFromMemory();
        } catch (err) {
            if (err && err.name === "AbortError") {
                return;
            }
            const safeMessage = err instanceof Error ? err.message : "Failed to get a response from the assistant.";
            console.error("[Chatbot Send Error]", err);
            appendMessage("assistant", `I couldn't answer right now. ${safeMessage}`, "error");
            chatLog.push({
                role: "assistant",
                content: `ERROR: ${safeMessage}`,
                provider: "lm_studio",
                model: null,
                timestamp: nowIso(),
            });
            persistActiveSessionFromMemory();
        } finally {
            if (activeRequestController === requestController) {
                activeRequestController = null;
            }
            removeThinkingBubble();
            if (generationAtStart === renderGeneration) {
                setSendingState(false);
                inputEl.focus();
                scrollToBottom();
            }
        }
    }

    function clearChat() {
        // Clears only the active session messages while keeping the session in the sidebar.
        stopCurrentInteraction();

        chatLog.length = 0;
        conversationHistory.length = 0;

        const active = getActiveSession();
        if (active) {
            active.chatLog = [];
            active.conversationHistory = [];
            active.title = "New chat";
            active.preview = "No messages yet";
            active.updatedAt = nowIso();
            saveStoredSessions();
        }

        renderSessionsSidebar();
        renderThreadFromMemory();
        inputEl.value = "";
        inputEl.focus();
    }

    function exportLogs() {
        if (!chatLog.length) {
            appendMessage("assistant", "No chat messages to export yet. Send a message first.", "export");
            return;
        }

        const lines = [
            "Sansevieria Chat Export",
            `Session: ${activeSessionId || "unknown"}`,
            `Generated: ${nowIso()}`,
            "",
            ...chatLog.map((item) => {
                const when = item.timestamp || "";
                const who = item.role === "user" ? "You" : "Sansevieria AI";
                return `[${when}] ${who}: ${item.content}`;
            }),
            "",
        ];

        const blob = new Blob([lines.join("\n")], { type: "text/plain;charset=utf-8" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `sansevieria-chat-${new Date().toISOString().replace(/:/g, "-")}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    sendBtn.addEventListener("click", sendMessage);
    inputEl.addEventListener("keydown", (event) => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    });
    clearBtn.addEventListener("click", clearChat);
    exportBtn.addEventListener("click", exportLogs);
    newChatBtn.addEventListener("click", startNewChat);

    removeStaticSamples();
    ensureSessionState();
    renderSessionsSidebar();
    renderThreadFromMemory();
    loadChatReadiness();
    scrollToBottom();
})();
