// ============================================================
// Вкладки карточки компании
// ============================================================

function activateTab(name) {
    document.querySelectorAll(".tab").forEach(function (btn) {
        btn.classList.toggle("active", btn.dataset.tab === name);
    });

    document.querySelectorAll(".pane").forEach(function (pane) {
        pane.classList.toggle("active", pane.dataset.pane === name);
    });
}

document.querySelectorAll(".tab").forEach(function (btn) {
    btn.addEventListener("click", function () {
        activateTab(btn.dataset.tab);

        try {
            const url = new URL(window.location.href);
            url.searchParams.set("tab", btn.dataset.tab);
            window.history.replaceState({}, "", url.toString());
        } catch (e) {}
    });
});

(function initTabFromUrl() {
    const params = new URLSearchParams(window.location.search);
    const tab = params.get("tab");
    if (tab && document.querySelector('.tab[data-tab="' + tab + '"]')) {
        activateTab(tab);
    }
})();


// ============================================================
// Подтверждение удаления
// ============================================================

document.querySelectorAll("[data-confirm]").forEach(function (btn) {
    btn.addEventListener("click", function (event) {
        if (!window.confirm(btn.getAttribute("data-confirm"))) {
            event.preventDefault();
        }
    });
});


// ============================================================
// Автозакрытие уведомлений
// ============================================================

document.querySelectorAll(".flash").forEach(function (flash) {
    setTimeout(function () {
        if (flash.parentElement) {
            flash.style.transition = "opacity .3s";
            flash.style.opacity = "0";
            setTimeout(function () { flash.remove(); }, 300);
        }
    }, 9000);
});


// ============================================================
// Форма контакта: создание / редактирование
// ============================================================

(function initContactForm() {
    const form = document.getElementById("contactForm");
    if (!form) return;

    const reset = function () {
        document.getElementById("contact_id").value = "";
        document.getElementById("contact_full_name").value = "";
        document.getElementById("contact_position").value = "";
        document.getElementById("contact_phone").value = "";
        document.getElementById("contact_email").value = "";
        document.getElementById("contact_primary").checked = false;
        document.getElementById("contactFormTitle").textContent = "Новый контакт";
    };

    document.getElementById("resetContactForm").addEventListener("click", reset);

    document.querySelectorAll("[data-edit-contact]").forEach(function (btn) {
        btn.addEventListener("click", function () {
            document.getElementById("contact_id").value = btn.dataset.id;
            document.getElementById("contact_full_name").value = btn.dataset.fullName || "";
            document.getElementById("contact_position").value = btn.dataset.position || "";
            document.getElementById("contact_phone").value = btn.dataset.phone || "";
            document.getElementById("contact_email").value = btn.dataset.email || "";
            document.getElementById("contact_primary").checked = btn.dataset.primary === "1";

            document.getElementById("contactFormTitle").textContent = "Редактирование контакта";

            form.scrollIntoView({ behavior: "smooth", block: "center" });
            document.getElementById("contact_full_name").focus();
        });
    });
})();


// ============================================================
// Поиск по правилам ОКВЭД
// ============================================================

(function initRuleFilter() {
    const input = document.getElementById("ruleFilter");
    const table = document.getElementById("rulesTable");
    if (!input || !table) return;

    input.addEventListener("input", function () {
        const query = input.value.trim().toLowerCase();

        table.querySelectorAll("tbody tr").forEach(function (row) {
            const text = (row.dataset.search || "").toLowerCase();
            row.style.display = !query || text.includes(query) ? "" : "none";
        });
    });
})();


// ============================================================
// Копирование текста письма
// ============================================================

(function initCopyMail() {
    const btn = document.getElementById("copyMailBody");
    if (!btn) return;

    btn.addEventListener("click", async function () {
        const textarea = document.querySelector('textarea[name="body"]');
        if (!textarea) return;

        try {
            await navigator.clipboard.writeText(textarea.value);
            btn.textContent = "Скопировано ✓";
            setTimeout(function () { btn.textContent = "Скопировать текст"; }, 2000);
        } catch (e) {
            textarea.select();
            document.execCommand("copy");
            btn.textContent = "Скопировано ✓";
        }
    });
})();


// ============================================================
// Опрос фоновой задачи загрузки Checko
// ============================================================

function pollJob(jobId, fallbackUrl) {
    const bar = document.getElementById("progressBar");
    const message = document.getElementById("fetchMessage");
    const title = document.getElementById("fetchTitle");
    const icon = document.getElementById("fetchIcon");
    const errorBox = document.getElementById("fetchError");
    const logBox = document.getElementById("fetchLog");

    let stopped = false;
    let lastMessage = "";
    let elapsedTimer = null;

    function startElapsed() {
        const started = Date.now();
        const el = document.getElementById("fetchElapsed");
        if (!el) return;
        elapsedTimer = setInterval(function () {
            const s = Math.floor((Date.now() - started) / 1000);
            el.textContent = "Прошло времени: " + Math.floor(s / 60) + " мин " + (s % 60) + " с";
        }, 1000);
    }

    function appendLog(message) {
        if (!logBox || !message || message === lastMessage) return;
        lastMessage = message;
        const time = new Date().toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
        const row = document.createElement("div");
        row.className = "fetch-log-row";
        row.textContent = "[" + time + "] " + message;
        logBox.appendChild(row);
        // keeping the log box scrollable and not infinitely long
        while (logBox.children.length > 50) logBox.removeChild(logBox.firstChild);
        logBox.scrollTop = logBox.scrollHeight;
    }

    function tick() {
        if (stopped) return;

        fetch("/jobs/" + jobId, { credentials: "same-origin" })
            .then(function (response) {
                if (!response.ok) {
                    throw new Error("HTTP " + response.status);
                }
                return response.json();
            })
            .then(function (job) {
                if (bar) bar.style.width = (job.progress || 0) + "%";
                if (message) message.textContent = job.message || "";
                appendLog(job.message);

                if (job.status === "done") {
                    stopped = true;
                    if (elapsedTimer) clearInterval(elapsedTimer);
                    if (title) title.textContent = "Компания готова";
                    if (icon) icon.textContent = "✅";

                    setTimeout(function () {
                        if (job.company_id) {
                            window.location.href = "/company/" + job.company_id + "?tab=okved";
                        } else {
                            window.location.href = fallbackUrl;
                        }
                    }, 900);
                    return;
                }

                if (job.status === "error") {
                    stopped = true;
                    if (elapsedTimer) clearInterval(elapsedTimer);
                    if (title) title.textContent = "Не удалось загрузить";
                    if (icon) icon.textContent = "⚠️";

                    if (errorBox) {
                        errorBox.style.display = "flex";
                        errorBox.textContent = job.error || "Неизвестная ошибка.";
                    }
                    // даём ссылку на карточку, чтобы вернуться к существующей компании
                    if (job.company_id) {
                        var backLink = document.getElementById("fetchBackLink");
                        if (backLink) {
                            backLink.href = "/company/" + job.company_id;
                            backLink.textContent = "Открыть карточку компании";
                            backLink.style.display = "inline-block";
                        }
                    }
                    return;
                }

                setTimeout(tick, 1800);
            })
            .catch(function (err) {
                console.warn("pollJob:", err);
                setTimeout(tick, 3000);
            });
    }

    startElapsed();
    setTimeout(tick, 600);
}