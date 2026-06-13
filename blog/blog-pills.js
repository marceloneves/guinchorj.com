(function () {
  "use strict";

  var pendingFilter = null;
  var pendingPill = null;

  function getCards() {
    var grid = document.getElementById("blog-posts-grid");
    if (!grid) {
      return null;
    }
    return grid.querySelectorAll("[data-category]");
  }

  function applyFilter(filter) {
    var cards = getCards();
    if (!cards || !cards.length) {
      return null;
    }

    var visible = 0;
    cards.forEach(function (card) {
      var show = filter === "all" || card.getAttribute("data-category") === filter;
      card.classList.toggle("blog-card-hidden", !show);
      if (show) {
        card.style.removeProperty("display");
        visible += 1;
      } else {
        card.style.setProperty("display", "none", "important");
      }
    });
    return visible;
  }

  function setActivePill(pill) {
    if (!pill) {
      return;
    }
    document.querySelectorAll(".blog-pill").forEach(function (item) {
      var active = item === pill;
      item.classList.toggle("is-active", active);
      item.setAttribute("aria-pressed", active ? "true" : "false");
    });
  }

  function updateCount(filter, visible) {
    var countEl = document.getElementById("blog-pills-count");
    var emptyEl = document.getElementById("blog-pills-empty");

    if (emptyEl) {
      emptyEl.classList.toggle("is-visible", visible === 0);
    }

    if (!countEl) {
      return;
    }

    if (filter === "all") {
      countEl.textContent = visible + " artigos";
      return;
    }

    var labelEl = document.querySelector('.blog-pill[data-filter="' + filter + '"]');
    countEl.textContent =
      visible + " artigos em " + (labelEl ? labelEl.textContent.trim() : "categoria selecionada");
  }

  function runFilter(filter, pill) {
    if (!pill) {
      pill = document.querySelector('.blog-pill[data-filter="' + filter + '"]');
    }
    if (!pill) {
      return false;
    }

    var visible = applyFilter(filter);
    if (visible === null) {
      pendingFilter = filter;
      pendingPill = pill;
      setActivePill(pill);
      return false;
    }

    pendingFilter = null;
    pendingPill = null;
    setActivePill(pill);
    updateCount(filter, visible);

    try {
      if (filter !== "all") {
        history.replaceState(null, "", "#" + filter);
      } else {
        history.replaceState(null, "", location.pathname);
      }
    } catch (error) {
      /* noop */
    }

    return false;
  }

  window.blogFilterClick = function (filter, pill) {
    return runFilter(filter, pill || null);
  };

  function boot() {
    if (pendingFilter) {
      runFilter(pendingFilter, pendingPill);
      return;
    }

    var hash = location.hash.replace(/^#/, "");
    if (hash && document.querySelector('.blog-pill[data-filter="' + hash + '"]')) {
      runFilter(hash, null);
      return;
    }

    var visible = applyFilter("all");
    if (visible !== null) {
      updateCount("all", visible);
    }
  }

  function watchGrid() {
    if (!window.MutationObserver || document.getElementById("blog-posts-grid")) {
      boot();
      return;
    }

    var observer = new MutationObserver(function () {
      if (document.getElementById("blog-posts-grid")) {
        observer.disconnect();
        boot();
      }
    });

    observer.observe(document.documentElement, { childList: true, subtree: true });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", watchGrid);
  } else {
    watchGrid();
  }

  document.addEventListener("rocket-DOMContentLoaded", boot);
})();
