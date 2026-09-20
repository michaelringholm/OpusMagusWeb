document.addEventListener("DOMContentLoaded", function() {
    // Smooth scroll for anchor links
    document.querySelectorAll("a[href^=\"#\"]").forEach(anchor => {
        anchor.addEventListener("click", function(e) {
            const href = this.getAttribute("href");
            if (href !== "#") {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({ behavior: "smooth" });
                }
            }
        });
    });

    // Lazy load images
    if ("IntersectionObserver" in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src || img.src;
                    img.classList.add("loaded");
                    observer.unobserve(img);
                }
            });
        });
        document.querySelectorAll("img[data-src]").forEach(img => imageObserver.observe(img));
    }

    // Focus management
    document.addEventListener("keydown", function(e) {
        if (e.key === "Escape") {
            document.activeElement.blur();
        }
    });
});
