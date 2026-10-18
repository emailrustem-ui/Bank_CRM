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
// Опрос фонового задачи загрузки Checko
// ============================================================

function pollJob(jobId, fallbackUrl) {
    const bar = document.getElementById("progressBar");
    const message = document.getElementById("fetchMessage");
    const title = document.getElementById("fetchTitle");
    const icon = document.getElementById("fetchIcon");
    const errorBox = document.getElementById("fetchError");
    const logBox = document.getElementById("fetchLog");

    let stopped = false;

    function tick() {
        if (stopped) return;

        fetch("/jobs/" + jobId, { credentials: "same-origin" })
            .then(function (response) { return response.json(); })
            .then(function (job) {
                if (bar) bar.style.width = (job.progress || 0) + "%";
                if (message) message.textContent = job.message || "";
                if (logBox && job.message) logBox.textContent = job.message;

                if (job.status === "done") {
                    stopped = true;
                    if (title) title.textContent = "Компания готова";
                    if (icon) icon.textContent = "✅";

                    setTimeout(function () {
                        window.location.href = "/company/" + job.company_id + "?tab=okved";
                    }, 900);
                    return;
                }

                if (job.status === "error") {
                    stopped = true;
                    if (title) title.textContent = "Не удалось загрузить";
                    if (icon) icon.textContent = "⚠️";

                    if (errorBox) {
                        errorBox.style.display = "flex";
                        errorBox.textContent = job.error || "Неизвестная ошибка.";
                    }
                    return;
                }

                setTimeout(tick, 1800);
            })
            .catch(function () {
                setTimeout(tick, 3000);
            });
    }

    setTimeout(tick, 1200);
}