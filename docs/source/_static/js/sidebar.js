window.addEventListener("load", () => {
    const current = document.querySelector(".sidebar-tree .current-page");
    const box = document.querySelector(".sidebar-scroll");
    if (!current || !box) return;
    const offset = current.getBoundingClientRect().top - box.getBoundingClientRect().top;
    box.scrollTo({ top: box.scrollTop + offset - box.clientHeight / 2 + current.clientHeight / 2, behavior: "instant" });
});
