/**
 * Wire clearance forms (sticky header + clearance landing confirm) to POST /api/clearance.
 */
(function () {
  "use strict";

  if (!window.RadspionClearanceRedeem) {
    return;
  }

  var wire = window.RadspionClearanceRedeem.wireClearanceForm;
  document.querySelectorAll(".clearance-form, .clearance-confirm-form").forEach(wire);
})();
