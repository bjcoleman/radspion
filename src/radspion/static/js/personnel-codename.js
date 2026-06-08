/**
 * Personnel File codename update — outcome modal + POST /api/codename.
 */
(function (global) {
  "use strict";

  var LENGTH_MESSAGE = "Codenames must be 4–20 characters.";
  var UNCHANGED_MESSAGE = "Your codename is unchanged.";
  var NETWORK_MESSAGE = "Update could not be completed. Try again.";

  var OK_BUTTON = '<button type="button" class="transmission-modal__ok">OK</button>';

  function escapeHtml(text) {
    var div = global.document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  function markSrc(modal) {
    return modal ? modal.getAttribute("data-mark-src") || "" : "";
  }

  function outcomeHeaderHtml(modal, line1, line2, variant) {
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
      escapeHtml(markSrc(modal)) +
      '" width="48" height="48" alt="">' +
      '<h2 id="codename-modal-heading" class="transmission-modal__outcome-heading">' +
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

  function codenameLengthValid(value) {
    var length = value.length;
    return length >= 4 && length <= 20;
  }

  function openModal(modal) {
    modal.hidden = false;
    global.document.body.classList.add("has-codename-modal");
  }

  function closeModal(modal) {
    modal.hidden = true;
    global.document.body.classList.remove("has-codename-modal");
  }

  function showOutcome(modal, outcomeEl, line1, line2, variant, message, onOk) {
    outcomeEl.innerHTML =
      outcomeHeaderHtml(modal, line1, line2, variant) +
      '<p class="transmission-modal__message">' +
      escapeHtml(message) +
      "</p>" +
      OK_BUTTON;

    openModal(modal);

    var ok = outcomeEl.querySelector(".transmission-modal__ok");
    if (!ok) {
      return;
    }
    ok.focus();
    ok.addEventListener(
      "click",
      function () {
        closeModal(modal);
        if (onOk) {
          onOk();
        }
      },
      { once: true },
    );
  }

  function postCodename(codename) {
    return fetch("/api/codename", {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ codename: codename }),
    }).then(function (response) {
      return response.json().then(function (data) {
        if (response.status === 401) {
          global.location.assign("/");
          return { outcome: "invalid", message: NETWORK_MESSAGE };
        }
        if (!response.ok) {
          throw new Error("codename update failed");
        }
        return data;
      });
    });
  }

  function wireCodenameForm(form, modal) {
    var outcomeEl = modal.querySelector("[data-codename-outcome]");
    if (!outcomeEl) {
      return;
    }

    form.addEventListener("submit", function (event) {
      event.preventDefault();

      var input = form.querySelector('[name="codename"]');
      var trimmed = input ? input.value.trim() : "";
      var current = form.getAttribute("data-current-codename") || "";

      if (trimmed === current) {
        showOutcome(
          modal,
          outcomeEl,
          "Codename",
          "Unchanged",
          "already_done",
          UNCHANGED_MESSAGE,
        );
        return;
      }

      if (!codenameLengthValid(trimmed)) {
        showOutcome(
          modal,
          outcomeEl,
          "Verification",
          "Failed",
          "failure",
          LENGTH_MESSAGE,
        );
        return;
      }

      postCodename(trimmed)
        .then(function (data) {
          if (data.outcome === "success") {
            showOutcome(
              modal,
              outcomeEl,
              "Codename",
              "Updated",
              "success",
              data.message || "Your codename has been updated.",
              function () {
                if ("scrollRestoration" in global.history) {
                  global.history.scrollRestoration = "manual";
                }
                global.location.reload();
              },
            );
            return;
          }

          showOutcome(
            modal,
            outcomeEl,
            "Verification",
            "Failed",
            "failure",
            data.message || LENGTH_MESSAGE,
          );
        })
        .catch(function () {
          showOutcome(
            modal,
            outcomeEl,
            "Verification",
            "Failed",
            "failure",
            NETWORK_MESSAGE,
          );
        });
    });
  }

  function init() {
    var form = global.document.querySelector("[data-personnel-codename-form]");
    var modal = global.document.querySelector("[data-codename-modal]");
    if (form && modal) {
      wireCodenameForm(form, modal);
    }
  }

  if (global.document.readyState === "loading") {
    global.document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})(window);
