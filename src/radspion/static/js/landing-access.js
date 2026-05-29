/**
 * Landing page: access-code form → POST /api/access → transmission modal.
 */
(function () {
  "use strict";

  var INVALID_FALLBACK =
    "We could not validate that access code against agency records.";

  var GOOGLE_ICON_SVG =
    '<svg class="btn-google__icon" viewBox="0 0 48 48" aria-hidden="true">' +
    '<path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>' +
    '<path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>' +
    '<path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>' +
    '<path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>' +
    "</svg>";

  function renderSuccess(outcomeEl) {
    outcomeEl.innerHTML =
      '<h2 class="transmission-modal__title">Clearance confirmed</h2>' +
      '<p class="transmission-modal__message">' +
      "Access code accepted. Continue with Google to verify your identity." +
      "</p>" +
      '<a href="#" class="btn-google btn-google--agent-login">' +
      GOOGLE_ICON_SVG +
      "Continue with Google</a>";
  }

  function renderInvalid(outcomeEl, message) {
    outcomeEl.innerHTML =
      '<h2 class="transmission-modal__title">Validation failed</h2>' +
      '<p class="transmission-modal__message"></p>' +
      '<button type="button" class="transmission-modal__ok">OK</button>';
    outcomeEl.querySelector(".transmission-modal__message").textContent =
      message || INVALID_FALLBACK;
  }

  function postAccess(accessCode) {
    return fetch("/api/access", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ access_code: accessCode }),
    }).then(function (response) {
      return response.json().then(function (data) {
        if (!response.ok) {
          var err = new Error("access request failed");
          err.status = response.status;
          err.data = data;
          throw err;
        }
        return data;
      });
    });
  }

  var form = document.querySelector(".access-panel__form");
  if (!form || !window.RadspionTransmission) {
    return;
  }

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    var input = form.querySelector('[name="access_code"]');
    var accessCode = input ? input.value : "";

    window.RadspionTransmission.transmit({
      preset: window.RadspionTransmission.PRESET.ACCESS_CODE,
      request: function () {
        return postAccess(accessCode).catch(function () {
          return { outcome: "invalid", message: INVALID_FALLBACK };
        });
      },
      renderOutcome: function (data, outcomeEl) {
        if (data.outcome === "success") {
          renderSuccess(outcomeEl);
          return;
        }
        renderInvalid(outcomeEl, data.message);
      },
    });
  });
})();
