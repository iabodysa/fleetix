document.documentElement.classList.add("js");
document.addEventListener("DOMContentLoaded", () => {
  const root = document.querySelector(".et");
  const stage = document.querySelector(".et-stage");
  const burger = document.querySelector(".et-burger");
  const reveals = document.querySelectorAll("[data-reveal]");
  if ("IntersectionObserver" in window) {
    new IntersectionObserver(([entry]) => root.classList.toggle("et--solid", !entry.isIntersecting), { rootMargin: "-64px 0px 0px 0px" }).observe(stage);
    const io = new IntersectionObserver((entries) => entries.forEach((entry) => {
      if (entry.isIntersecting) { entry.target.classList.add("is-visible"); io.unobserve(entry.target); }
    }), { threshold: 0.15 });
    reveals.forEach((el) => io.observe(el));
  } else {
    root.classList.add("et--solid");
    reveals.forEach((el) => el.classList.add("is-visible"));
  }
  const setMenu = (open) => {
    root.classList.toggle("et--menu", open);
    document.body.classList.toggle("et-lock", open);
    burger.setAttribute("aria-expanded", String(open));
    burger.setAttribute("aria-label", open ? burger.dataset.closeLabel : burger.dataset.openLabel);
  };
  burger.addEventListener("click", () => setMenu(!root.classList.contains("et--menu")));
  document.querySelectorAll(".et-nav a").forEach((a) => a.addEventListener("click", () => setMenu(false)));
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") setMenu(false); });
});
