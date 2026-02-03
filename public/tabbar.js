document.querySelectorAll(".mobile-tabbar").forEach((bar) => {
    const moreBtn = bar.querySelector(".tab-more");
    const menu = bar.querySelector(".more-menu");
    if (!moreBtn || !menu) return;

    moreBtn.addEventListener("click", () => {
        const isOpen = menu.classList.toggle("open");
        moreBtn.setAttribute("aria-expanded", isOpen ? "true" : "false");
    });

    menu.querySelectorAll("a").forEach((link) => {
        link.addEventListener("click", () => {
            menu.classList.remove("open");
            moreBtn.setAttribute("aria-expanded", "false");
        });
    });
});
