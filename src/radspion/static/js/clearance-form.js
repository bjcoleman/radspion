/**
 * Wire clearance forms (sticky header + unlock landing confirm) to POST /api/unlock.
 */
(function () {
  "use strict";

  if (!window.RadspionUnlockRedeem) {
    return;
  }

  var wire = window.RadspionUnlockRedeem.wireClearanceForm;
  document.querySelectorAll(".clearance-form, .unlock-confirm-form").forEach(wire);
})();
