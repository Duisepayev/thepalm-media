// Меню на телефоне и события для Google Tag Manager (клики WhatsApp, звонок, маршрут).
(function () {
  var burger = document.querySelector(".burger");
  var nav = document.getElementById("nav");
  if (burger && nav) {
    burger.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      burger.setAttribute("aria-expanded", open ? "true" : "false");
    });
    nav.addEventListener("click", function (ev) {
      if (ev.target.tagName === "A") nav.classList.remove("open");
    });
  }

  window.dataLayer = window.dataLayer || [];
  document.addEventListener("click", function (ev) {
    var a = ev.target.closest && ev.target.closest("[data-track]");
    if (!a) return;
    window.dataLayer.push({
      event: a.getAttribute("data-track"),
      cta_location: a.getAttribute("data-where") || "",
      cta_topic: a.getAttribute("data-topic") || "",
      page_path: location.pathname
    });
  });
})();
