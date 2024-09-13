document.addEventListener("DOMContentLoaded", function () {
  // Make extendList function global
  window.extendList = function () {
    document.getElementById("extended-list").style.display = "block";
    document.getElementById("extend-button").style.display = "none";
    showBackToTopButton();
  };

  function showBackToTopButton() {
    const backToTop = document.getElementById("backToTop");
    backToTop.style.display = "block";
    setTimeout(() => (backToTop.style.opacity = "1"), 50);

    window.addEventListener("scroll", () => {
      backToTop.style.display = window.scrollY > 200 ? "block" : "none";
    });

    backToTop.addEventListener("click", () => {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  const showAllButton = document.getElementById("extend-button");
  if (showAllButton) {
    showAllButton.addEventListener("click", window.extendList);
  }
});
