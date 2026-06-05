/**
 * After QR clearance + OAuth, play the same transmission modal as manual clearance.
 */
(function () {
  "use strict";

  var data = window.RADSPION_POST_LOGIN_CLEARANCE;
  if (!data || !window.RadspionClearanceRedeem) {
    return;
  }

  delete window.RADSPION_POST_LOGIN_CLEARANCE;
  window.RadspionClearanceRedeem.showClearanceResult(data);
})();
