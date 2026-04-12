(function () {
    const apiHost = (typeof API_BASE !== "undefined") ? API_BASE : "http://localhost:8000";
    const chatEndpoint = `${apiHost}/api/chat/`;

    const messagesEl = document.getElementById("chatMessages");
    const inputEl = document.getElementById("chatInput");
    const sendBtn = document.getElementById("sendMessageBtn");
    const clearBtn = document.getElementById("clearChatBtn");
    const exportBtn = document.getElementById("exportLogsBtn");
    const greetingEl = document.getElementById("chatGreeting");

    if (!messagesEl || !inputEl || !sendBtn || !clearBtn || !exportBtn) {
        return;
    }

    const initialGreetingHTML = greetingEl ? greetingEl.outerHTML : "";
    const chatLog = [];
    const conversationHistory = [];
    const MEMORY_LIMIT = 8; // Last 8 role messages (~4 user/assistant exchanges).
    let isSending = false;
    let activeRequestController = null;
    let renderGeneration = 0;

    function getAccessToken() {
        return localStorage.getItem("access_token");
    }

    function scrollToBottom() {
        messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    function escapeHtml(text) {
        return String(text)
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll("\"", "&quot;")
            .replaceAll("'", "&#39;");
    }

    function buildUserMessageHtml(text) {
        return `
            <div class="flex flex-row-reverse items-start gap-4 chat-dynamic-message" data-role="user">
                <div class="w-10 h-10 rounded-lg bg-slate-200 dark:bg-slate-700 flex items-center justify-center shrink-0">
                    <span class="material-symbols-outlined text-slate-500 dark:text-slate-400 text-xl">person</span>
                </div>
                <div class="flex flex-col gap-1.5 max-w-[80%] items-end">
                    <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">You</p>
                    <div class="bg-primary text-slate-900 p-4 rounded-xl rounded-tr-none font-medium break-words whitespace-pre-wrap">
                        ${escapeHtml(text)}
                    </div>
                </div>
            </div>
        `;
    }

    function buildAssistantMessageHtml(text, metaText) {
        return `
            <div class="flex items-start gap-4 chat-dynamic-message" data-role="assistant">
                <div class="w-10 h-10 rounded-lg bg-primary flex items-center justify-center shrink-0">
                    <span class="material-symbols-outlined text-white text-xl">psychology</span>
                </div>
                <div class="flex flex-col gap-1.5 max-w-[80%]">
                    <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Sansevieria AI</p>
                    <div class="chat-message-content bg-primary/10 dark:bg-primary/5 text-slate-800 dark:text-slate-200 p-4 rounded-xl rounded-tl-none border border-primary/10 break-words whitespace-pre-wrap">
                        ${escapeHtml(text)}
                    </div>
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

    function removeStaticSamples() {
        messagesEl.querySelectorAll('[data-static-chat="sample"]').forEach((el) => el.remove());
    }

    function removeGreetingIfNeeded() {
        const currentGreeting = document.getElementById("chatGreeting");
        if (currentGreeting && currentGreeting.parentElement) {
            currentGreeting.remove();
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

        contentEl.textContent = text;
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
            timestamp: new Date().toISOString(),
        });
        conversationHistory.push({
            role: "user",
            content: message,
        });
        trimConversationHistory();

        inputEl.value = "";
        setSendingState(true);
        addThinkingBubble();
        const requestController = new AbortController();
        activeRequestController = requestController;

        try {
            const requestMessages = [
                ...conversationHistory.slice(-MEMORY_LIMIT),
            ];
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
                timestamp: new Date().toISOString(),
            });
            conversationHistory.push({
                role: "assistant",
                content: assistantText,
            });
            trimConversationHistory();
        } catch (err) {
            if (err && err.name === "AbortError") {
                return;
            }
            const safeMessage = err instanceof Error ? err.message : "Failed to get a response from the assistant.";
            appendMessage("assistant", `I couldn't answer right now. ${safeMessage}`, "error");
            chatLog.push({
                role: "assistant",
                content: `ERROR: ${safeMessage}`,
                provider: "lm_studio",
                model: null,
                timestamp: new Date().toISOString(),
            });
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
        renderGeneration += 1;
        if (activeRequestController) {
            activeRequestController.abort();
            activeRequestController = null;
        }
        messagesEl.querySelectorAll(".chat-dynamic-message").forEach((el) => el.remove());
        removeThinkingBubble();
        if (!messagesEl.querySelector("#chatGreeting") && initialGreetingHTML) {
            const wrap = document.createElement("div");
            wrap.innerHTML = initialGreetingHTML;
            const greetingNode = wrap.firstElementChild;
            if (greetingNode) {
                messagesEl.prepend(greetingNode);
            }
        }
        chatLog.length = 0;
        conversationHistory.length = 0;
        setSendingState(false);
        inputEl.value = "";
        inputEl.focus();
        scrollToBottom();
    }

    function exportLogs() {
        if (!chatLog.length) {
            appendMessage("assistant", "No chat messages to export yet. Send a message first.", "export");
            return;
        }

        const lines = [
            "Sansevieria Chat Export",
            `Generated: ${new Date().toISOString()}`,
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
        a.download = `sansevieria-chat-${new Date().toISOString().replaceAll(":", "-")}.txt`;
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

    removeStaticSamples();
    scrollToBottom();
})();
