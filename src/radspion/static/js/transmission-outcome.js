/**
 * Shared transmission modal outcome chrome (stacked headings, mission groups).
 */
(function (global) {
  "use strict";

  function escapeHtml(text) {
    var div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  function markSrc() {
    var modal = global.document.querySelector("[data-transmission-modal]");
    return modal ? modal.getAttribute("data-mark-src") || "" : "";
  }

  function outcomeHeaderHtml(line1, line2, variant) {
    var markClass = "transmission-modal__outcome-mark";
    if (variant === "failure") {
      markClass += " transmission-modal__outcome-mark--failure";
    } else if (variant === "already_done") {
      markClass += " transmission-modal__outcome-mark--already-done";
    } else {
      markClass += " transmission-modal__outcome-mark--success";
    }

    return (
      '<div class="transmission-modal__outcome-header">' +
      '<img class="' +
      markClass +
      '" src="' +
      escapeHtml(markSrc()) +
      '" width="48" height="48" alt="">' +
      '<h2 class="transmission-modal__outcome-heading">' +
      '<span class="transmission-modal__outcome-heading-line">' +
      escapeHtml(line1) +
      "</span>" +
      '<span class="transmission-modal__outcome-heading-line">' +
      escapeHtml(line2) +
      "</span>" +
      "</h2>" +
      "</div>"
    );
  }

  function missionGroupsHtml(newMissions) {
    if (!newMissions.length) {
      return "";
    }

    var groups = [];
    var groupMap = Object.create(null);
    newMissions.forEach(function (mission) {
      var name = mission.group_name || "Missions";
      if (!groupMap[name]) {
        groupMap[name] = [];
        groups.push(name);
      }
      groupMap[name].push(mission);
    });

    var sections = groups
      .map(function (groupName) {
        var items = groupMap[groupName]
          .map(function (mission) {
            return (
              '<li class="outcome-missions__item">' +
              escapeHtml(mission.title) +
              ' <span class="outcome-missions__slug text-mono">(' +
              escapeHtml(mission.slug) +
              ")</span></li>"
            );
          })
          .join("");

        return (
          '<section class="outcome-missions-group">' +
          '<h3 class="outcome-missions-group__heading">' +
          escapeHtml(groupName) +
          "</h3>" +
          '<ul class="outcome-missions">' +
          items +
          "</ul>" +
          "</section>"
        );
      })
      .join("");

    return '<div class="outcome-missions-groups">' + sections + "</div>";
  }

  function disableScrollRestoration() {
    if ("scrollRestoration" in global.history) {
      global.history.scrollRestoration = "manual";
    }
  }

  function dashboardUrl() {
    var modal = global.document.querySelector("[data-transmission-modal]");
    return modal ? modal.getAttribute("data-dashboard-url") || "" : "";
  }

  function wireOkCallback(outcomeEl, callback) {
    var ok = outcomeEl.querySelector(".transmission-modal__ok");
    if (!ok) {
      return;
    }
    ok.addEventListener("click", callback, { once: true });
  }

  function wireOkReloadTop(outcomeEl) {
    wireOkCallback(outcomeEl, function () {
      disableScrollRestoration();
      global.location.reload();
    });
  }

  function wireOkNavigateTop(outcomeEl, url) {
    if (!url) {
      return;
    }
    wireOkCallback(outcomeEl, function () {
      disableScrollRestoration();
      global.location.assign(url);
    });
  }

  var OK_BUTTON = '<button type="button" class="transmission-modal__ok">OK</button>';

  global.RadspionTransmissionOutcome = {
    escapeHtml: escapeHtml,
    outcomeHeaderHtml: outcomeHeaderHtml,
    missionGroupsHtml: missionGroupsHtml,
    dashboardUrl: dashboardUrl,
    wireOkReloadTop: wireOkReloadTop,
    wireOkNavigateTop: wireOkNavigateTop,
    okButton: OK_BUTTON,
  };
})(window);
