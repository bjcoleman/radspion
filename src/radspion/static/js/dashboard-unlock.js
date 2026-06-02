/**
 * Agent dashboard: unlock-code form → POST /api/unlock → transmission modal.
 */
(function () {
  "use strict";

  var form = document.querySelector(".unlock-form");
  if (!form || !window.RadspionUnlockRedeem) {
    return;
  }

  window.RadspionUnlockRedeem.wireDashboardForm(form);
})();
