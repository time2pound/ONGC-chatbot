// ==========================================================================
// ONGC AI Assistant - JavaScript logic
// Tab Management, Chat Sessions, Voice API, Ingestion, & Analytics Feed
// ==========================================================================

document.addEventListener("DOMContentLoaded", () => {
    // App State
    let activeTab = "chat-view";
    let activeSessionId = null;
    let sessions = []; // array of {id, name}
    let availableModels = [];
    
    // Voice Settings
    let textToSpeechEnabled = false;
    let recognition = null;
    let isListening = false;

    // DOM Elements
    const navItems = document.querySelectorAll(".nav-item");
    const viewPanels = document.querySelectorAll(".view-panel");
    const viewTitle = document.getElementById("view-title");
    const viewSubtitle = document.getElementById("view-subtitle");
    
    const chatFeed = document.getElementById("chat-feed");
    const chatForm = document.getElementById("chat-form");
    const chatInput = document.getElementById("chat-input");
    const newChatBtn = document.getElementById("new-chat-btn");
    const sessionList = document.getElementById("session-list");
    const chatActiveModelLabel = document.getElementById("chat-active-model");
    
    const themeToggle = document.getElementById("theme-toggle");
    
    // Ingest View Elements
    const uploadZone = document.getElementById("upload-zone");
    const fileInput = document.getElementById("file-input");
    const progressContainer = document.getElementById("upload-progress-container");
    const progressBar = document.getElementById("upload-progress");
    const uploadAlert = document.getElementById("upload-alert");
    const documentTableBody = document.getElementById("document-table-body");
    
    // Settings View Elements
    const settingModel = document.getElementById("setting-model");
    const settingTemp = document.getElementById("setting-temp");
    const tempVal = document.getElementById("temp-val");
    const settingK = document.getElementById("setting-k");
    const saveSettingsBtn = document.getElementById("save-settings-btn");
    const clearDbBtn = document.getElementById("clear-db-btn");
    
    // Analytics View Elements
    const statTotalChats = document.getElementById("stat-total-chats");
    const statLikes = document.getElementById("stat-likes");
    const statDislikes = document.getElementById("stat-dislikes");
    const statSatisfaction = document.getElementById("stat-satisfaction");
    const commentsFeed = document.getElementById("comments-feed");
    const logFeed = document.getElementById("log-feed");
    
    // Feedback Modal Elements
    const feedbackModal = document.getElementById("feedback-modal");
    const feedbackComment = document.getElementById("feedback-comment");
    const closeModal = document.getElementById("close-modal");
    const cancelFeedbackBtn = document.getElementById("cancel-feedback-btn");
    const submitFeedbackBtn = document.getElementById("submit-feedback-btn");
    
    // Voice Elements
    const voiceInputBtn = document.getElementById("voice-input-btn");
    const voiceOutputToggle = document.getElementById("voice-output-toggle");

    // Last message info for feedback reference
    let lastExchange = {
        question: "",
        answer: ""
    };

    // ==========================================
    // 1. Initial configuration load & UI Setup
    // ==========================================
    
    // Load local storage settings
    let config = {
        model: localStorage.getItem("ongc_model") || "llama3.2:1b",
        temperature: parseFloat(localStorage.getItem("ongc_temp") || "0.0"),
        k: parseInt(localStorage.getItem("ongc_k") || "5")
    };

    // Update settings DOM controls
    settingTemp.value = config.temperature;
    tempVal.textContent = config.temperature.toFixed(1);
    settingK.value = config.k;
    chatActiveModelLabel.textContent = config.model;

    // Load available models from API
    async function loadModels() {
        try {
            const res = await fetch("/api/models");
            const data = await res.json();
            availableModels = data.models || [];
            
            // Populate select box
            settingModel.innerHTML = "";
            availableModels.forEach(m => {
                const opt = document.createElement("option");
                opt.value = m;
                opt.textContent = m;
                if (m === config.model) opt.selected = true;
                settingModel.appendChild(opt);
            });
            
            // Check if active model exists, if not, choose first
            if (availableModels.length > 0 && !availableModels.includes(config.model)) {
                config.model = availableModels[0];
                localStorage.setItem("ongc_model", config.model);
            }
            // Always update the header label to reflect loaded models
            chatActiveModelLabel.textContent = config.model;
        } catch (e) {
            console.error("Failed to load models list", e);
        }
    }

    // Auto resize textarea
    chatInput.addEventListener("input", function() {
        this.style.height = "auto";
        this.style.height = (this.scrollHeight) + "px";
    });

    // Temp slider label sync
    settingTemp.addEventListener("input", function() {
        tempVal.textContent = parseFloat(this.value).toFixed(1);
    });

    // Save Settings
    saveSettingsBtn.addEventListener("click", () => {
        config.model = settingModel.value;
        config.temperature = parseFloat(settingTemp.value);
        config.k = parseInt(settingK.value);
        
        localStorage.setItem("ongc_model", config.model);
        localStorage.setItem("ongc_temp", config.temperature);
        localStorage.setItem("ongc_k", config.k);
        
        chatActiveModelLabel.textContent = config.model;
        showBanner("Configuration saved successfully!", "success", "settings-view");
    });

    // Reset database / clear local storage sessions
    clearDbBtn.addEventListener("click", () => {
        if (confirm("Are you sure you want to clear all chat sessions? This cannot be undone.")) {
            sessions = [];
            localStorage.removeItem("ongc_sessions");
            activeSessionId = null;
            renderSessions();
            initNewSession();
            showBanner("Chat history reset successfully!", "success", "settings-view");
        }
    });

    // Theme Switch
    themeToggle.addEventListener("click", () => {
        const currentTheme = document.documentElement.getAttribute("data-theme");
        const nextTheme = currentTheme === "dark" ? "light" : "dark";
        document.documentElement.setAttribute("data-theme", nextTheme);
        
        const themeIcon = themeToggle.querySelector("i");
        const themeText = themeToggle.querySelector("span");
        
        if (nextTheme === "light") {
            themeIcon.className = "fa-solid fa-sun";
            themeText.textContent = "Light Mode";
        } else {
            themeIcon.className = "fa-solid fa-moon";
            themeText.textContent = "Dark Mode";
        }
    });

    // ==========================================
    // 2. Navigation Tabs
    // ==========================================
    
    navItems.forEach(item => {
        item.addEventListener("click", (e) => {
            e.preventDefault();
            const tabId = item.getAttribute("data-tab");
            switchTab(tabId);
        });
    });

    function switchTab(tabId) {
        activeTab = tabId;
        
        // Update nav UI
        navItems.forEach(i => i.classList.remove("active"));
        document.querySelector(`.nav-item[data-tab="${tabId}"]`).classList.add("active");
        
        // Update View Panels
        viewPanels.forEach(p => p.classList.remove("active"));
        document.getElementById(tabId).classList.add("active");
        
        // Set Header descriptions
        if (tabId === "chat-view") {
            viewTitle.textContent = "Chat Hub";
            viewSubtitle.textContent = "Access corporate documents via local AI";
        } else if (tabId === "docs-view") {
            viewTitle.textContent = "Documents Manager";
            viewSubtitle.textContent = "Index, update, and manage indexed PDF manuals";
            loadDocuments();
        } else if (tabId === "analytics-view") {
            viewTitle.textContent = "Analytics Dashboard";
            viewSubtitle.textContent = "Visual representation of feedback and usage reports";
            loadAnalytics();
        } else if (tabId === "settings-view") {
            viewTitle.textContent = "Configuration Panel";
            viewSubtitle.textContent = "Modify retrieval strategies and deep parameters";
            loadModels();
        }
    }

    // ==========================================
    // 3. Chat Session Management
    // ==========================================
    
    function loadSessions() {
        const cached = localStorage.getItem("ongc_sessions");
        if (cached) {
            sessions = JSON.parse(cached);
        } else {
            sessions = [];
        }
        renderSessions();
        
        if (sessions.length > 0) {
            selectSession(sessions[0].id);
        } else {
            initNewSession();
        }
    }

    function saveSessions() {
        localStorage.setItem("ongc_sessions", JSON.stringify(sessions));
    }

    function renderSessions() {
        sessionList.innerHTML = "";
        sessions.forEach(s => {
            const div = document.createElement("div");
            div.className = `session-item ${s.id === activeSessionId ? "active" : ""}`;
            div.setAttribute("data-id", s.id);
            div.innerHTML = `
                <span class="session-name"><i class="fa-regular fa-message"></i> ${s.name}</span>
                <button class="session-delete-btn" title="Delete Session"><i class="fa-solid fa-trash-can"></i></button>
            `;
            
            // Delete action
            div.querySelector(".session-delete-btn").addEventListener("click", (e) => {
                e.stopPropagation();
                deleteSession(s.id);
            });
            
            // Click to select
            div.addEventListener("click", () => {
                selectSession(s.id);
            });
            
            sessionList.appendChild(div);
        });
    }

    function initNewSession() {
        const id = "session_" + Date.now();
        const newSession = {
            id: id,
            name: "New Conversation",
            history: []
        };
        sessions.unshift(newSession);
        activeSessionId = id;
        saveSessions();
        renderSessions();
        clearChatFeed();
    }

    function selectSession(id) {
        activeSessionId = id;
        renderSessions();
        clearChatFeed();
        
        // Retrieve and load history from LocalStorage session
        const session = sessions.find(s => s.id === id);
        if (session && session.history && session.history.length > 0) {
            session.history.forEach(h => {
                renderMessage(h.role, h.content, h.sources, false);
            });
            // Auto scroll to bottom
            chatFeed.scrollTop = chatFeed.scrollHeight;
        }
    }

    function deleteSession(id) {
        sessions = sessions.filter(s => s.id !== id);
        saveSessions();
        
        if (activeSessionId === id) {
            if (sessions.length > 0) {
                selectSession(sessions[0].id);
            } else {
                initNewSession();
            }
        } else {
            renderSessions();
        }
    }

    function clearChatFeed() {
        chatFeed.innerHTML = `
            <div class="welcome-box">
                <div class="welcome-icon">
                    <i class="fa-solid fa-microchip"></i>
                </div>
                <h3>Welcome to ONGC AI Knowledge Assistant</h3>
                <p>Query policies, rules, and manuals from our indexed PDF knowledge base. To get started, ask a question or check the suggestions below.</p>
                
                <div class="suggestions-grid">
                    <button class="suggest-card" data-prompt="What is the role of Policy Monitoring and Control (PMC) Section?">
                        <i class="fa-solid fa-compass"></i>
                        <span>PMC Section Role</span>
                    </button>
                    <button class="suggest-card" data-prompt="What is the inventory level check policy for materials procurement?">
                        <i class="fa-solid fa-boxes-stacked"></i>
                        <span>Inventory Check Policy</span>
                    </button>
                    <button class="suggest-card" data-prompt="Where and when is the Integrated Materials Management Manual applicable?">
                        <i class="fa-solid fa-book-open"></i>
                        <span>Manual Applicability</span>
                    </button>
                    <button class="suggest-card" data-prompt="Who is responsible for reviewing tender documents?">
                        <i class="fa-solid fa-gavel"></i>
                        <span>Tender Document Review</span>
                    </button>
                </div>
            </div>
        `;
        
        // Rebind suggest cards
        const suggestCards = chatFeed.querySelectorAll(".suggest-card");
        suggestCards.forEach(card => {
            card.addEventListener("click", () => {
                chatInput.value = card.getAttribute("data-prompt");
                chatInput.focus();
                chatForm.dispatchEvent(new Event("submit"));
            });
        });
    }

    // ==========================================
    // 4. Chat Processing & Core RAG Pipeline
    // ==========================================
    
    chatForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const text = chatInput.value.trim();
        if (!text) return;
        
        chatInput.value = "";
        chatInput.style.height = "auto";
        
        // Remove welcome box if present
        const welcome = chatFeed.querySelector(".welcome-box");
        if (welcome) welcome.remove();
        
        // Update Session name if default
        const currentSession = sessions.find(s => s.id === activeSessionId);
        if (currentSession && currentSession.name === "New Conversation") {
            currentSession.name = text.length > 25 ? text.substring(0, 25) + "..." : text;
            saveSessions();
            renderSessions();
        }

        // Render user message
        renderMessage("user", text, null, true);
        
        // Render typing indicator
        const typingId = renderTypingIndicator();
        chatFeed.scrollTop = chatFeed.scrollHeight;

        try {
            // Post payload
            const res = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    question: text,
                    model: config.model,
                    temperature: config.temperature,
                    session_id: activeSessionId
                })
            });
            
            // Remove typing indicator
            const typingEl = document.getElementById(typingId);
            if (typingEl) typingEl.remove();

            if (!res.ok) {
                const err = await res.json();
                renderMessage("assistant", `Error: ${err.detail || "Server encountered error."}`, null, true);
                return;
            }

            const data = await res.json();
            
            // Save last exchange for feedback submission
            lastExchange = {
                question: text,
                answer: data.answer
            };
            
            // Render AI response
            renderMessage("assistant", data.answer, data.sources, true);
            
            // Append message history locally to session cache
            if (currentSession) {
                if (!currentSession.history) currentSession.history = [];
                currentSession.history.push({ role: "user", content: text });
                currentSession.history.push({ role: "assistant", content: data.answer, sources: data.sources });
                saveSessions();
            }

            // Auto Speech Synthesis if enabled
            if (textToSpeechEnabled) {
                speakText(data.answer);
            }

        } catch (e) {
            console.error(e);
            const typingEl = document.getElementById(typingId);
            if (typingEl) typingEl.remove();
            renderMessage("assistant", `Error: Failed to connect to server. Check local console.`, null, true);
        }
        
        chatFeed.scrollTop = chatFeed.scrollHeight;
    });

    newChatBtn.addEventListener("click", () => {
        initNewSession();
    });

    function renderTypingIndicator() {
        const id = "typing_" + Date.now();
        const row = document.createElement("div");
        row.className = "message-row assistant";
        row.id = id;
        row.innerHTML = `
            <div class="message-bubble">
                <div class="typing-indicator">
                    <span class="typing-dot"></span>
                    <span class="typing-dot"></span>
                    <span class="typing-dot"></span>
                </div>
            </div>
        `;
        chatFeed.appendChild(row);
        return id;
    }

    function renderMessage(role, text, sources, animate) {
        const row = document.createElement("div");
        row.className = `message-row ${role}`;
        
        // Escape HTML
        let formattedText = escapeHTML(text);
        // Quick basic formatting of bold and lists
        formattedText = formatMarkdown(formattedText);
        
        let sourcesHtml = "";
        let feedbackHtml = "";
        
        if (role === "assistant") {
            // Render Sources if present
            if (sources && sources.length > 0) {
                const uniqueId = "sources_" + Date.now() + "_" + Math.floor(Math.random() * 1000);
                let itemsHtml = "";
                sources.forEach(src => {
                    itemsHtml += `
                        <div class="source-item">
                            <div class="source-meta">
                                <span class="filename"><i class="fa-solid fa-file-invoice"></i> ${src.filename}</span>
                                <span class="page-num">${src.page}</span>
                            </div>
                            <div class="source-snippet">${escapeHTML(src.snippet)}</div>
                        </div>
                    `;
                });
                
                sourcesHtml = `
                    <div class="sources-container">
                        <div class="sources-toggle" onclick="toggleSources('${uniqueId}', this)">
                            <i class="fa-solid fa-chevron-down"></i> Retrieved References (${sources.length})
                        </div>
                        <div class="sources-content" id="${uniqueId}">
                            ${itemsHtml}
                        </div>
                    </div>
                `;
            }
            
            // Render feedback options
            feedbackHtml = `
                <div class="feedback-actions">
                    <span>Was this helpful?</span>
                    <button class="feedback-btn up" onclick="handleFeedbackClick('up', this)" title="Helpful"><i class="fa-regular fa-thumbs-up"></i></button>
                    <button class="feedback-btn down" onclick="handleFeedbackClick('down', this)" title="Unhelpful"><i class="fa-regular fa-thumbs-down"></i></button>
                </div>
            `;
        }

        row.innerHTML = `
            <div class="message-bubble">
                <div class="message-text">${formattedText}</div>
                ${sourcesHtml}
                ${feedbackHtml}
            </div>
        `;
        
        chatFeed.appendChild(row);
        
        // Text animation for AI responses if enabled
        if (role === "assistant" && animate) {
            // Simple micro-animation
            row.style.animation = "slideUp 0.3s ease-out";
        }
    }

    // Helper functions for formatting RAG output
    function escapeHTML(str) {
        return str
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    function formatMarkdown(text) {
        // Convert Markdown Bold
        text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        // Convert bullet points
        const lines = text.split("\n");
        let inList = false;
        let output = "";
        
        lines.forEach(line => {
            // Checks for bullets: "- " or "* " or "1. "
            if (line.trim().startsWith("- ") || line.trim().startsWith("* ")) {
                if (!inList) {
                    output += "<ul>";
                    inList = true;
                }
                output += `<li>${line.trim().substring(2)}</li>`;
            } else {
                if (inList) {
                    output += "</ul>";
                    inList = false;
                }
                output += `<p>${line}</p>`;
            }
        });
        
        if (inList) output += "</ul>";
        return output;
    }

    // Dynamic global trigger scope
    window.toggleSources = (id, el) => {
        el.classList.toggle("open");
        const panel = document.getElementById(id);
        panel.classList.toggle("open");
    };

    window.handleFeedbackClick = async (type, btn) => {
        const row = btn.closest(".message-bubble");
        const promptText = row.querySelector(".message-text").textContent;
        
        // Set highlights
        const upBtn = row.querySelector(".feedback-btn.up");
        const downBtn = row.querySelector(".feedback-btn.down");
        
        upBtn.classList.remove("active");
        downBtn.classList.remove("active");
        
        btn.classList.add("active");
        
        if (type === "up") {
            // Submit direct success feedback
            try {
                await fetch("/api/feedback", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        session_id: activeSessionId,
                        question: lastExchange.question || "Unknown",
                        answer: lastExchange.answer || promptText,
                        rating: "up",
                        comment: "User rated positive"
                    })
                });
            } catch (e) {
                console.error("Feedback error", e);
            }
        } else {
            // Trigger feedback modal for explanation comments
            feedbackComment.value = "";
            feedbackModal.classList.add("open");
            
            // Bind submit btn inside modal once
            submitFeedbackBtn.onclick = async () => {
                feedbackModal.classList.remove("open");
                const comment = feedbackComment.value.trim();
                
                try {
                    await fetch("/api/feedback", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                            session_id: activeSessionId,
                            question: lastExchange.question || "Unknown",
                            answer: lastExchange.answer || promptText,
                            rating: "down",
                            comment: comment || "User rated negative"
                        })
                    });
                } catch (e) {
                    console.error("Feedback error", e);
                }
            };
        }
    };

    // Close Modal triggers
    closeModal.onclick = () => feedbackModal.classList.remove("open");
    cancelFeedbackBtn.onclick = () => feedbackModal.classList.remove("open");

    // ==========================================
    // 5. Ingestion & Documents View
    // ==========================================
    
    // Drag & Drop
    ["dragenter", "dragover"].forEach(eventName => {
        uploadZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            uploadZone.classList.add("dragover");
        }, false);
    });

    ["dragleave", "drop"].forEach(eventName => {
        uploadZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            uploadZone.classList.remove("dragover");
        }, false);
    });

    uploadZone.addEventListener("drop", (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            handleFileUpload(files[0]);
        }
    });

    uploadZone.addEventListener("click", () => {
        fileInput.click();
    });

    fileInput.addEventListener("change", () => {
        if (fileInput.files.length > 0) {
            handleFileUpload(fileInput.files[0]);
        }
    });

    function handleFileUpload(file) {
        if (!file.name.endsWith(".pdf")) {
            showUploadAlert("Only PDF manual files are accepted.", "error");
            return;
        }
        
        // Reset Progress bar
        uploadAlert.style.display = "none";
        progressContainer.style.display = "block";
        progressBar.style.width = "0%";
        progressBar.textContent = "0%";
        
        const xhr = new XMLHttpRequest();
        const formData = new FormData();
        formData.append("file", file);
        
        xhr.open("POST", "/api/ingest", true);
        
        // Progress listener
        xhr.upload.addEventListener("progress", (e) => {
            if (e.lengthComputable) {
                const percent = Math.round((e.loaded / e.total) * 100);
                // Limit to 95% during parsing, 100% on complete confirmation
                const showPercent = Math.min(percent, 95);
                progressBar.style.width = showPercent + "%";
                progressBar.textContent = `Uploading & Indexing: ${showPercent}%`;
            }
        });
        
        xhr.onreadystatechange = () => {
            if (xhr.readyState === 4) {
                progressContainer.style.display = "none";
                if (xhr.status === 200) {
                    const data = JSON.parse(xhr.responseText);
                    progressBar.style.width = "100%";
                    showUploadAlert(`Successfully indexed "${data.filename}" (${data.chunks_created} context chunks created).`, "success");
                    loadDocuments();
                } else {
                    let errMsg = "Ingestion failed.";
                    try {
                        const err = JSON.parse(xhr.responseText);
                        errMsg = err.detail || errMsg;
                    } catch (errEval) {}
                    showUploadAlert(errMsg, "error");
                }
            }
        };
        
        xhr.send(formData);
    }

    function showUploadAlert(msg, type) {
        uploadAlert.className = `alert-box ${type}`;
        uploadAlert.innerHTML = `
            <i class="fa-solid ${type === 'success' ? 'fa-circle-check' : 'fa-circle-exclamation'}"></i>
            <span>${msg}</span>
        `;
        uploadAlert.style.display = "block";
    }

    async function loadDocuments() {
        try {
            const res = await fetch("/api/documents");
            const data = await res.json();
            const docsList = data.documents || [];
            
            documentTableBody.innerHTML = "";
            
            if (docsList.length === 0) {
                documentTableBody.innerHTML = `
                    <tr>
                        <td colspan="3" class="text-center">No documents currently indexed. Go ahead and upload one above!</td>
                    </tr>
                `;
                return;
            }
            
            docsList.forEach(d => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td><strong>${escapeHTML(d)}</strong></td>
                    <td>PDF Manual File</td>
                    <td><span class="status-tag active">Indexed</span></td>
                `;
                documentTableBody.appendChild(tr);
            });
        } catch (e) {
            console.error(e);
            documentTableBody.innerHTML = `
                <tr>
                    <td colspan="3" class="text-center text-danger">Error fetching document registry from server.</td>
                </tr>
            `;
        }
    }

    // ==========================================
    // 6. Analytics Dashboard
    // ==========================================
    
    async function loadAnalytics() {
        try {
            const res = await fetch("/api/analytics");
            const data = await res.json();
            
            // Set Stat Cards
            statTotalChats.textContent = data.total_chats || 0;
            statLikes.textContent = data.likes || 0;
            statDislikes.textContent = data.dislikes || 0;
            statSatisfaction.textContent = data.satisfaction_rate || "N/A";
            
            // Populate Comments Feed
            commentsFeed.innerHTML = "";
            const recentComments = data.user_comments || [];
            if (recentComments.length === 0) {
                commentsFeed.innerHTML = `<div class="empty-state">No comments submitted yet.</div>`;
            } else {
                recentComments.forEach(c => {
                    const el = document.createElement("div");
                    el.className = "comment-card";
                    // Format timestamp
                    const t = new Date(c.timestamp).toLocaleString();
                    el.innerHTML = `
                        <div class="comment-meta">
                            <span><i class="fa-regular fa-user"></i> ONGC User</span>
                            <span>${t}</span>
                        </div>
                        <div class="comment-text">"${escapeHTML(c.comment)}"</div>
                    `;
                    commentsFeed.appendChild(el);
                });
            }
            
            // Populate Log Feed
            logFeed.innerHTML = "";
            const recentLogs = data.recent_activity || [];
            if (recentLogs.length === 0) {
                logFeed.innerHTML = `<div class="empty-state">No activity logged yet.</div>`;
            } else {
                recentLogs.forEach(l => {
                    const el = document.createElement("div");
                    el.className = "log-item";
                    const ratingTag = l.rating === "up" 
                        ? `<span class="log-rating-tag up"><i class="fa-regular fa-thumbs-up"></i> Helpful</span>`
                        : `<span class="log-rating-tag down"><i class="fa-regular fa-thumbs-down"></i> Unhelpful</span>`;
                    
                    const t = new Date(l.timestamp).toLocaleTimeString();
                    el.innerHTML = `
                        <div class="log-left">
                            <span class="log-question" title="${escapeHTML(l.question)}">${escapeHTML(l.question)}</span>
                            <span class="log-time">${t}</span>
                        </div>
                        <div class="log-right">
                            ${ratingTag}
                        </div>
                    `;
                    logFeed.appendChild(el);
                });
            }
            
        } catch (e) {
            console.error("Failed to load analytics feedback feed", e);
        }
    }

    // ==========================================
    // 7. Voice Interface (Speech API)
    // ==========================================
    
    // HTML5 Speech Synthesis (Text to Speech)
    function speakText(text) {
        if (!('speechSynthesis' in window)) return;
        
        // Cancel ongoing synthesis
        window.speechSynthesis.cancel();
        
        // Strip markdown tags and URLs for clean read
        const cleanText = text.replace(/<[^>]*>/g, '').replace(/\[.*?\]\(.*?\)/g, '');
        
        const utterance = new SpeechSynthesisUtterance(cleanText);
        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        
        // Pick premium voice if available
        const voices = window.speechSynthesis.getVoices();
        const defaultVoice = voices.find(v => v.name.includes("Google US English") || v.name.includes("Microsoft Zira") || v.lang === "en-US");
        if (defaultVoice) utterance.voice = defaultVoice;
        
        window.speechSynthesis.speak(utterance);
    }
    
    voiceOutputToggle.addEventListener("click", () => {
        textToSpeechEnabled = !textToSpeechEnabled;
        const icon = voiceOutputToggle.querySelector("i");
        
        if (textToSpeechEnabled) {
            icon.className = "fa-solid fa-volume-up";
            voiceOutputToggle.style.backgroundColor = "rgba(242, 169, 0, 0.15)";
            voiceOutputToggle.style.color = "var(--brand-gold)";
            voiceOutputToggle.style.borderColor = "var(--brand-gold)";
        } else {
            icon.className = "fa-solid fa-volume-mute";
            voiceOutputToggle.style.backgroundColor = "var(--bg-secondary)";
            voiceOutputToggle.style.color = "var(--text-secondary)";
            voiceOutputToggle.style.borderColor = "var(--border-color)";
            
            // Stop current speech
            if ('speechSynthesis' in window) {
                window.speechSynthesis.cancel();
            }
        }
    });
    
    // HTML5 Speech Recognition (Speech to Text)
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = "en-US";
        
        recognition.onstart = () => {
            isListening = true;
            voiceInputBtn.classList.add("active");
            chatInput.placeholder = "Listening... Speak your question now.";
        };
        
        recognition.onend = () => {
            isListening = false;
            voiceInputBtn.classList.remove("active");
            chatInput.placeholder = "Ask about ONGC manuals...";
        };
        
        recognition.onerror = (e) => {
            console.error("Speech Recognition Error", e);
            isListening = false;
            voiceInputBtn.classList.remove("active");
            chatInput.placeholder = "Speech error. Try again.";
        };
        
        recognition.onresult = (e) => {
            const transcript = e.results[0][0].transcript;
            chatInput.value = transcript;
            // Force textarea resize
            chatInput.dispatchEvent(new Event("input"));
        };
        
        voiceInputBtn.addEventListener("click", () => {
            if (isListening) {
                recognition.stop();
            } else {
                recognition.start();
            }
        });
    } else {
        // Hide button if browser doesn't support
        voiceInputBtn.style.display = "none";
    }

    // UI Helpers
    function showBanner(msg, type, panelId) {
        const p = document.getElementById(panelId);
        const alert = document.createElement("div");
        alert.className = `alert-box ${type}`;
        alert.style.margin = "0 0 20px 0";
        alert.innerHTML = `
            <i class="fa-solid ${type === 'success' ? 'fa-circle-check' : 'fa-circle-exclamation'}"></i>
            <span>${msg}</span>
        `;
        p.insertBefore(alert, p.firstChild);
        setTimeout(() => alert.remove(), 4000);
    }

    // ==========================================
    // 8. Initialization Run
    // ==========================================
    
    loadModels();
    loadSessions();
});
