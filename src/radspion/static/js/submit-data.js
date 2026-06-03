/**
 * Field data submission: header form, link confirm, POST /api/submit, modal outcomes.
 */
(function (global) {
  "use strict";

  var INVALID_FALLBACK =
    "We could not validate that data against agency records.";

  function escapeHtml(text) {
    var div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  function singleMissionMessage(mission) {
    return (
      "The following mission was added to your dashboard: " +
      "<strong>" +
      escapeHtml(mission.title) +
      "</strong>."
    );
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

  function renderOutcomeShell(title, messageHtml) {
    return function (outcomeEl) {
      outcomeEl.innerHTML =
        '<h2 class="transmission-modal__title">' +
        escapeHtml(title) +
        "</h2>" +
        '<p class="transmission-modal__message">' +
        messageHtml +
        "</p>" +
        '<button type="button" class="transmission-modal__ok">OK</button>';
    };
  }

  function renderListSuccess(outcomeEl, newMissions) {
    if (newMissions.length <= 1) {
      var messageHtml = newMissions.length
        ? singleMissionMessage(newMissions[0])
        : "Data accepted.";
      renderOutcomeShell("Transmission accepted", messageHtml)(outcomeEl);
      return;
    }

    outcomeEl.innerHTML =
      '<h2 class="transmission-modal__title">Transmission accepted</h2>' +
      '<p class="transmission-modal__message">' +
      "The following missions were added to your dashboard:" +
      "</p>" +
      '<ul class="transmission-modal__mission-list">' +
      missionListItemsHtml(newMissions) +
      "</ul>" +
      '<button type="button" class="transmission-modal__ok">OK</button>';
  }

  function renderCompleteSuccess(outcomeEl, newMissions) {
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
  }

  function renderInvalid(outcomeEl, message) {
    renderOutcomeShell(
      "Verification failed",
      escapeHtml(message || INVALID_FALLBACK),
    )(outcomeEl);
  }

  function renderAlreadyDone(outcomeEl, data) {
    if (data.kind === "complete") {
      renderOutcomeShell(
        "Already complete",
        escapeHtml(data.message || "This mission is already marked complete."),
      )(outcomeEl);
      return;
    }
    renderOutcomeShell(
      "Already on your dashboard",
      escapeHtml(data.message || "Those missions are already on your dashboard."),
    )(outcomeEl);
  }

  function renderSubmitOutcome(data, outcomeEl) {
    if (data.outcome === "success") {
      if (data.kind === "complete") {
        renderCompleteSuccess(outcomeEl, data.new_missions || []);
      } else {
        renderListSuccess(outcomeEl, data.new_missions || []);
      }
      return;
    }
    if (data.outcome === "already_done") {
      renderAlreadyDone(outcomeEl, data);
      return;
    }
    renderInvalid(outcomeEl, data.message);
  }

  function postData(value) {
    return fetch("/api/submit", {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ data: value }),
    }).then(function (response) {
      return response.json().then(function (data) {
        if (response.status === 401) {
          global.location.assign("/");
          return { outcome: "invalid", message: INVALID_FALLBACK };
        }
        if (!response.ok) {
          throw new Error("submit request failed");
        }
        return data;
      });
    });
  }

  function redirectAfterSuccess(result) {
    if (result.kind === "complete" && result.mission_slug) {
      global.location.assign(
        "/agent/missions/" + encodeURIComponent(result.mission_slug),
      );
      return;
    }
    global.location.assign("/agent/dashboard");
  }

  function runSubmitTransmission(options) {
    if (!global.RadspionTransmission) {
      return;
    }
    global.RadspionTransmission.transmitSerialized({
      request: options.request,
      renderOutcome: renderSubmitOutcome,
      redirectOnSuccess: options.redirectOnSuccess !== false,
      onSuccess: options.onSuccess || redirectAfterSuccess,
    });
  }

  function submitFromInput(rawValue, options) {
    runSubmitTransmission({
      request: function () {
        return postData(rawValue).catch(function () {
          return { outcome: "invalid", message: INVALID_FALLBACK };
        });
      },
      redirectOnSuccess: options && options.redirectOnSuccess,
      onSuccess: options && options.onSuccess,
    });
  }

  function wireSubmitForm(form, options) {
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      var input = form.querySelector('[name="data"]');
      var value = input ? input.value : "";
      submitFromInput(value, options);
    });
  }

  function showStagedResult(data) {
    if (!global.RadspionTransmission) {
      return;
    }
    global.RadspionTransmission.presentOutcome({
      result: data,
      renderOutcome: renderSubmitOutcome,
    });
  }

  function initHeaderForm() {
    var form = global.document.querySelector(".site-header__submit");
    if (form) {
      wireSubmitForm(form);
    }
  }

  function initConfirmForms() {
    global.document.querySelectorAll(".data-submit-form--confirm").forEach(function (form) {
      wireSubmitForm(form);
    });
  }

  global.RadspionSubmit = {
    postData: postData,
    renderSubmitOutcome: renderSubmitOutcome,
    redirectAfterSuccess: redirectAfterSuccess,
    showStagedResult: showStagedResult,
    submitFromInput: submitFromInput,
    wireSubmitForm: wireSubmitForm,
  };

  initHeaderForm();
  initConfirmForms();
})(window);
