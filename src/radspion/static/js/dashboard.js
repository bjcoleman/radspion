/**
 * Agent dashboard: show/hide completed missions; collapse empty groups.
 */
(function () {
  "use strict";

  var toggle = document.querySelector("[data-show-completed]");
  if (!toggle) {
    return;
  }

  function updateGroupCounts(group, showCompleted) {
    var countsEl = group.querySelector("[data-group-counts]");
    if (!countsEl) {
      return;
    }
    var items = group.querySelectorAll("[data-mission-status]");
    var active = 0;
    var completed = 0;
    for (var i = 0; i < items.length; i++) {
      if (items[i].getAttribute("data-mission-status") === "active") {
        active += 1;
      } else if (items[i].getAttribute("data-mission-status") === "completed") {
        completed += 1;
      }
    }
    var parts = [];
    if (active) {
      parts.push(active + " active");
    }
    if (completed) {
      parts.push(
        completed + " completed" + (showCompleted ? "" : " (hidden)")
      );
    }
    countsEl.textContent = parts.join(" · ");
  }

  function applyVisibility() {
    var showCompleted = toggle.checked;
    var groups = document.querySelectorAll("[data-mission-group]");
    for (var g = 0; g < groups.length; g++) {
      var group = groups[g];
      var completedItems = group.querySelectorAll(".mission-list__item--completed");
      for (var i = 0; i < completedItems.length; i++) {
        completedItems[i].hidden = !showCompleted;
      }
      var visibleActive = group.querySelector(
        '.mission-list__item[data-mission-status="active"]:not([hidden])'
      );
      group.open = Boolean(visibleActive);
      updateGroupCounts(group, showCompleted);
    }
  }

  toggle.addEventListener("change", applyVisibility);
  applyVisibility();
})();
