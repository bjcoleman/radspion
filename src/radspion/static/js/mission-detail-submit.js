/**
 * Mission detail: completion form → POST /api/missions/<slug>/submit → transmission modal.
 */
(function () {
  "use strict";

  var INVALID_FALLBACK =
    "We reviewed your transmission, and the recovered data does not match mission requirements.";

  function escapeHtml(text) {
    var div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  function missionListItemsHtml(newMissions) {
    return newMissions
      .map(function (mission) {
        return (
          "<li><strong>" +
          escapeHtml(mission.title) +
          '</strong> <span class="text-mono">' +
          escapeHtml(mission.slug) +
          "</span></li>"
        );
      })
      .join("");
  }

  function wireOkReload(outcomeEl) {
    var ok = outcomeEl.querySelector(".transmission-modal__ok");
    if (!ok) {
      return;
    }
    ok.addEventListener(
      "click",
      function () {
        window.location.reload();
      },
      { once: true },
    );
  }

  function renderOutcomeShell(title, messageHtml, reloadOnOk) {
    return function (outcomeEl) {
      outcomeEl.innerHTML =
        '<h2 class="transmission-modal__title">' +
        escapeHtml(title) +
        "</h2>" +
        '<p class="transmission-modal__message">' +
        messageHtml +
        "</p>" +
        '<button type="button" class="transmission-modal__ok">OK</button>';
      if (reloadOnOk) {
        wireOkReload(outcomeEl);
      }
    };
  }

  function renderSuccess(outcomeEl, newMissions) {
    if (newMissions.length === 0) {
      outcomeEl.innerHTML =
        '<h2 class="transmission-modal__title">Transmission accepted</h2>' +
        '<p class="transmission-modal__message">' +
        "Lab verification confirmed your field data. This mission is now marked as completed." +
        "</p>" +
        '<p class="transmission-modal__message">' +
        "Read the debrief for your after-action summary." +
        "</p>" +
        '<button type="button" class="transmission-modal__ok">OK</button>';
      wireOkReload(outcomeEl);
      return;
    }

    outcomeEl.innerHTML =
      '<h2 class="transmission-modal__title">Transmission accepted</h2>' +
      '<p class="transmission-modal__message">' +
      "Lab verification confirmed your field data. This mission is now marked as completed." +
      "</p>" +
      '<p class="transmission-modal__message">' +
      "The following mission" +
      (newMissions.length === 1 ? " was" : "s were") +
      " added to your dashboard:" +
      "</p>" +
      '<ul class="transmission-modal__mission-list">' +
      missionListItemsHtml(newMissions) +
      "</ul>" +
      '<p class="transmission-modal__message">' +
      "Read the debrief for your after-action summary." +
      "</p>" +
      '<button type="button" class="transmission-modal__ok">OK</button>';
    wireOkReload(outcomeEl);
  }

  function renderInvalid(outcomeEl, message) {
    renderOutcomeShell(
      "Verification failed",
      escapeHtml(message || INVALID_FALLBACK),
      false,
    )(outcomeEl);
  }

  function renderAlreadyDone(outcomeEl, message) {
    renderOutcomeShell(
      "Already complete",
      escapeHtml(message || "This mission is already marked complete."),
      false,
    )(outcomeEl);
  }

  function postSubmit(slug, completionCode) {
    return fetch("/api/missions/" + encodeURIComponent(slug) + "/submit", {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ completion_code: completionCode }),
    }).then(function (response) {
      return response.json().then(function (data) {
        if (response.status === 401) {
          window.location.assign("/");
          return { outcome: "invalid", message: INVALID_FALLBACK };
        }
        if (response.status === 404) {
          return { outcome: "invalid", message: INVALID_FALLBACK };
        }
        if (!response.ok) {
          var err = new Error("submit request failed");
          err.status = response.status;
          err.data = data;
          throw err;
        }
        return data;
      });
    });
  }

  var form = document.querySelector(".completion-form");
  if (!form || !window.RadspionTransmission) {
    return;
  }

  var slug = form.getAttribute("data-mission-slug");
  if (!slug) {
    return;
  }

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    var input = form.querySelector('[name="completion_code"]');
    var completionCode = input ? input.value : "";

    window.RadspionTransmission.transmit({
      preset: window.RadspionTransmission.PRESET.COMPLETION_DATA,
      request: function () {
        return postSubmit(slug, completionCode).catch(function () {
          return { outcome: "invalid", message: INVALID_FALLBACK };
        });
      },
      renderOutcome: function (data, outcomeEl) {
        if (data.outcome === "success") {
          renderSuccess(outcomeEl, data.new_missions || []);
          return;
        }
        if (data.outcome === "already_done") {
          renderAlreadyDone(outcomeEl, data.message);
          return;
        }
        renderInvalid(outcomeEl, data.message);
      },
    });
  });
})();
