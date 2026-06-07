/**
 * Mission detail: copy buttons on brief/debrief code blocks and recovered data.
 */
(function () {
  "use strict";

  var COPY_ICON =
    '<svg class="copy-btn__icon" width="16" height="16" viewBox="0 0 24 24" aria-hidden="true" focusable="false">' +
    '<path fill="currentColor" d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/>' +
    "</svg>";

  function codeText(block) {
    var code = block.querySelector("code");
    return (code || block).textContent;
  }

  function wrapBlock(block, ariaLabel) {
    if (block.closest(".code-block")) {
      return;
    }

    var wrapper = document.createElement("div");
    wrapper.className = "code-block";
    block.parentNode.insertBefore(wrapper, block);
    wrapper.appendChild(block);

    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "copy-btn";
    btn.setAttribute("aria-label", ariaLabel || "Copy code to clipboard");
    btn.innerHTML = COPY_ICON;
    wrapper.insertBefore(btn, block);

    btn.addEventListener("click", function () {
      var text = codeText(block);
      if (!navigator.clipboard || !navigator.clipboard.writeText) {
        return;
      }
      navigator.clipboard.writeText(text).then(
        function () {
          btn.classList.add("copy-btn--copied");
          window.setTimeout(function () {
            btn.classList.remove("copy-btn--copied");
          }, 2000);
        },
        function () {},
      );
    });
  }

  function init() {
    document.querySelectorAll("article.mission-markdown").forEach(function (article) {
      article.querySelectorAll(".highlight").forEach(wrapBlock);
      article.querySelectorAll("pre").forEach(function (pre) {
        if (!pre.closest(".highlight")) {
          wrapBlock(pre);
        }
      });
    });

    document.querySelectorAll(".recovered-data__block pre.recovered-data__value").forEach(function (pre) {
      wrapBlock(pre, "Copy recovered data to clipboard");
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
