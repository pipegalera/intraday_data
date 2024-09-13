document.addEventListener("DOMContentLoaded", function () {
  // Throttle function to limit how often a function can fire
  function throttle(func, limit) {
    let inThrottle;
    return function () {
      const args = arguments;
      const context = this;
      if (!inThrottle) {
        func.apply(context, args);
        inThrottle = true;
        setTimeout(() => (inThrottle = false), limit);
      }
    };
  }

  // Make extendList function global
  window.extendList = function () {
    const extendedList = document.getElementById("extended-list");
    const extendButton = document.getElementById("extend-button");

    if (extendedList && extendButton) {
      extendedList.style.display = "block";
      extendButton.style.display = "none";
      showBackToTopButton();
    } else {
      console.error("Extended list or extend button not found");
    }
  };

  function showBackToTopButton() {
    const backToTop = document.getElementById("backToTop");
    if (!backToTop) {
      console.error("Back to top button not found");
      return;
    }

    backToTop.style.display = "block";
    setTimeout(() => (backToTop.style.opacity = "1"), 50);

    // Throttled scroll event listener
    window.addEventListener(
      "scroll",
      throttle(() => {
        const scrollTop =
          window.pageYOffset || document.documentElement.scrollTop;
        backToTop.style.display = scrollTop > 200 ? "block" : "none";
      }, 100),
    );

    backToTop.addEventListener("click", () => {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  // Optional: Add event listener to the "Show All" button
  const showAllButton = document.getElementById("extend-button");
  if (showAllButton) {
    showAllButton.addEventListener("click", window.extendList);
  } else {
    console.error("Show All button not found");
  }

  // Optional: Initialize back to top button if it's always present
  const backToTopButton = document.getElementById("backToTop");
  if (backToTopButton) {
    showBackToTopButton();
  }
});
