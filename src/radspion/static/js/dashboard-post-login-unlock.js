/**
 * After QR unlock + OAuth, play the same transmission modal as manual unlock.
 */
(function () {
  "use strict";

  var data = window.RADSPION_POST_LOGIN_UNLOCK;
  if (!data || !window.RadspionUnlockRedeem) {
    return;
  }

  delete window.RADSPION_POST_LOGIN_UNLOCK;
  window.RadspionUnlockRedeem.showUnlockResult(data);
})();
