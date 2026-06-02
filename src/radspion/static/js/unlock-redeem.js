/**
 * Shared mission unlock transmission modal (dashboard form + post-login QR redeem).
 */
(function (global) {
  "use strict";

  var INVALID_FALLBACK =
    "We could not validate that unlock code against agency records.";

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
    if (newMissions.length <= 1) {
      var messageHtml = newMissions.length
        ? singleMissionMessage(newMissions[0])
        : "Unlock code accepted.";
      renderOutcomeShell("Verification succeeded", messageHtml, true)(outcomeEl);
      return;
    }

    outcomeEl.innerHTML =
      '<h2 class="transmission-modal__title">Verification succeeded</h2>' +
      '<p class="transmission-modal__message">' +
      "The following missions were added to your dashboard:" +
      "</p>" +
      '<ul class="transmission-modal__mission-list">' +
      missionListItemsHtml(newMissions) +
      "</ul>" +
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
      "Already on your dashboard",
      escapeHtml(
        message || "Those missions are already on your dashboard.",
      ),
      false,
    )(outcomeEl);
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
          window.location.assign("/");
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

  function wireDashboardForm(form) {
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
    wireDashboardForm: wireDashboardForm,
  };
})(window);
