/**
 * Play the transmission modal once for a server-staged submit outcome.
 */
(function () {
  "use strict";

  var data = window.RADSPION_STAGED_SUBMIT_RESULT;
  if (!data || !window.RadspionSubmit) {
    return;
  }

  delete window.RADSPION_STAGED_SUBMIT_RESULT;
  window.RadspionSubmit.showStagedResult(data);
})();
