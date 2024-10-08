document.addEventListener("DOMContentLoaded", function () {
  console.log("DOM fully loaded and parsed");

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

  window.extendList = function () {
    console.log("extendList function called");
    const extendedList = document.getElementById("extended-list");
    const extendButton = document.getElementById("extend-button");
    const backToTopButton = document.getElementById("backToTop");

    console.log("Extended list:", extendedList);
    console.log("Extend button:", extendButton);
    console.log("Back to top button:", backToTopButton);

    if (extendedList && extendButton) {
      extendedList.style.display = "block";
      extendButton.style.display = "none";
      if (backToTopButton) {
        showBackToTopButton();
      } else {
        console.error("Back to top button not found");
      }
    } else {
      console.error("Extended list or extend button not found");
    }
  };

  function showBackToTopButton() {
    console.log("showBackToTopButton function called");
    const backToTop = document.getElementById("backToTop");
    if (!backToTop) {
      console.error("Back to top button not found");
      return;
    }

    backToTop.style.display = "block";
    backToTop.style.opacity = "1";

    const scrollHandler = throttle(() => {
      const scrollTop =
        window.pageYOffset || document.documentElement.scrollTop;
      backToTop.style.display = scrollTop > 200 ? "block" : "none";
    }, 100);

    window.addEventListener("scroll", scrollHandler);

    backToTop.addEventListener("click", () => {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  // Countdown function
  function startCountdown(duration) {
    const timerElement = document.getElementById("timer");
    if (!timerElement) {
      console.error("Timer element not found");
      return;
    }

    function updateCountdown() {
      const minutes = Math.floor(duration / 60);
      const seconds = duration % 60;
      timerElement.textContent = `${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`;

      if (duration > 0) {
        duration--;
        setTimeout(updateCountdown, 1000);
      } else {
        location.reload(); // Reload the page when countdown reaches zero
      }
    }

    updateCountdown();
  }

  // Initialize event listeners
  const showAllButton = document.getElementById("extend-button");
  if (showAllButton) {
    console.log("Adding click event listener to Show All button");
    showAllButton.addEventListener("click", window.extendList);
  } else {
    console.error("Show All button not found");
  }

  // Start the countdown
  const secondsToNextHour = parseInt(
    document.getElementById("seconds-to-next-hour").textContent,
    10,
  );
  startCountdown(secondsToNextHour);

  console.log("Script execution completed");
});
