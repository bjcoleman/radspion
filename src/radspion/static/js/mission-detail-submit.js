/**
 * Mission detail: data form → POST /api/missions/<slug>/submit → transmission modal.
 */
(function () {
  "use strict";

  var Outcome = window.RadspionTransmissionOutcome;

  var INVALID_FALLBACK =
    "We received your transmission, but the recovered data does not match mission " +
    "parameters. Continue your fieldwork and submit again when you have the correct value.";

  function renderSuccess(outcomeEl, newMissions) {
    var html =
      Outcome.outcomeHeaderHtml("Data", "Accepted", "success") +
      '<p class="transmission-modal__message">' +
      "Lab verification confirmed your field data. This mission is now marked as completed." +
      "</p>";

    if (newMissions.length > 0) {
      html +=
        '<p class="transmission-modal__message">' +
        "The data you recovered has produced additional missions:" +
        "</p>" +
        Outcome.missionGroupsHtml(newMissions);
    }

    html +=
      '<p class="transmission-modal__message">' +
      "Read the debrief for your after-action summary." +
      "</p>" +
      Outcome.okButton;

    outcomeEl.innerHTML = html;
    Outcome.wireOkReload(outcomeEl);
  }

  function renderInvalid(outcomeEl, message) {
    outcomeEl.innerHTML =
      Outcome.outcomeHeaderHtml("Verification", "Failed", "failure") +
      '<p class="transmission-modal__message">' +
      Outcome.escapeHtml(message || INVALID_FALLBACK) +
      "</p>" +
      Outcome.okButton;
  }

  function renderAlreadyDone(outcomeEl, message) {
    outcomeEl.innerHTML =
      Outcome.outcomeHeaderHtml("Previously", "Completed", "already_done") +
      '<p class="transmission-modal__message">' +
      Outcome.escapeHtml(message || "This mission is already marked complete.") +
      "</p>" +
      Outcome.okButton;
  }

  function postSubmit(slug, completionData) {
    return fetch("/api/missions/" + encodeURIComponent(slug) + "/submit", {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ completion_data: completionData }),
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
          throw new Error("submit request failed");
        }
        return data;
      });
    });
  }

  var form = document.querySelector(".recovered-data-form");
  if (!form || !window.RadspionTransmission) {
    return;
  }

  var slug = form.getAttribute("data-mission-slug");
  if (!slug) {
    return;
  }

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    var input = form.querySelector('[name="completion_data"]');
    var completionData = input ? input.value : "";

    window.RadspionTransmission.transmit({
      preset: window.RadspionTransmission.PRESET.COMPLETION_DATA,
      request: function () {
        return postSubmit(slug, completionData).catch(function () {
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
