// Direct 1-click theme toggler (Dark <-> Light)
document.addEventListener("click", (e) => {
    const btn = e.target.closest(".theme-toggle");
    if (!btn) return;
    e.stopPropagation();
    e.stopImmediatePropagation();
    e.preventDefault();
    const current = document.body.dataset.theme;
    const isDark = current === "dark" || (current !== "light" && window.matchMedia("(prefers-color-scheme: dark)").matches);
    const newTheme = isDark ? "light" : "dark";
    document.body.dataset.theme = newTheme;
    localStorage.setItem("theme", newTheme);
}, true);

window.addEventListener("load", () => {
    const current = document.querySelector(".sidebar-tree .current-page");
    const box = document.querySelector(".sidebar-scroll");
    if (!current || !box) return;
    const offset = current.getBoundingClientRect().top - box.getBoundingClientRect().top;
    box.scrollTo({ top: box.scrollTop + offset - box.clientHeight / 2 + current.clientHeight / 2, behavior: "instant" });
});

