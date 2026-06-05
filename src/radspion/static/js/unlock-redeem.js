/**
 * Clearance transmission modal (header form, unlock landing, post-login QR redeem).
 */
(function (global) {
  "use strict";

  var Outcome = global.RadspionTransmissionOutcome;

  var INVALID_FALLBACK =
    "Command could not verify this clearance code against agency records. Check the code and try again.";

  function renderSuccess(outcomeEl, newMissions) {
    outcomeEl.innerHTML =
      Outcome.outcomeHeaderHtml("Clearance", "Granted", "success") +
      '<p class="transmission-modal__message">' +
      "Your request for further clearance was approved, and Command has added the " +
      "following missions to your dashboard:" +
      "</p>" +
      Outcome.missionGroupsHtml(newMissions) +
      Outcome.okButton;
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
      Outcome.outcomeHeaderHtml("Previously", "Granted", "already_done") +
      '<p class="transmission-modal__message">' +
      Outcome.escapeHtml(
        message || "You have already been granted this clearance.",
      ) +
      "</p>" +
      Outcome.okButton;
  }

  function renderUnlockOutcome(data, outcomeEl) {
    if (data.outcome === "success") {
      renderSuccess(outcomeEl, data.new_missions || []);
      return;
    }
    if (data.outcome === "already_done") {
      renderAlreadyDone(outcomeEl, data.message);
      return;
    }
    renderInvalid(outcomeEl, data.message);
  }

  function postUnlock(unlockCode) {
    return fetch("/api/unlock", {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ unlock_code: unlockCode }),
    }).then(function (response) {
      return response.json().then(function (data) {
        if (response.status === 401) {
          global.location.assign("/");
          return { outcome: "invalid", message: INVALID_FALLBACK };
        }
        if (!response.ok) {
          throw new Error("unlock request failed");
        }
        return data;
      });
    });
  }

  function runUnlockTransmission(requestFn) {
    if (!global.RadspionTransmission) {
      return;
    }
    global.RadspionTransmission.transmit({
      preset: global.RadspionTransmission.PRESET.UNLOCK_CODE,
      request: requestFn,
      renderOutcome: renderUnlockOutcome,
    });
  }

  function showUnlockResult(data) {
    runUnlockTransmission(function () {
      return Promise.resolve(data);
    });
  }

  function wireClearanceForm(form) {
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      var input = form.querySelector('[name="unlock_code"]');
      var unlockCode = input ? input.value : "";

      runUnlockTransmission(function () {
        return postUnlock(unlockCode).catch(function () {
          return { outcome: "invalid", message: INVALID_FALLBACK };
        });
      });
    });
  }

  global.RadspionUnlockRedeem = {
    showUnlockResult: showUnlockResult,
    wireClearanceForm: wireClearanceForm,
    wireDashboardForm: wireClearanceForm,
  };
})(window);
