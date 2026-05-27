(function () {
  var COPIED_LABEL = "Copied";
  var DEFAULT_LABEL = "Copy to clipboard";

  function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(text);
    }
    var area = document.createElement("textarea");
    area.value = text;
    area.setAttribute("readonly", "");
    area.style.position = "fixed";
    area.style.left = "-9999px";
    document.body.appendChild(area);
    area.select();
    try {
      document.execCommand("copy");
      return Promise.resolve();
    } finally {
      document.body.removeChild(area);
    }
  }

  function getCopyTarget(button) {
    var block = button.closest(".code-block, .recovered-data__block");
    if (!block) return null;
    var code = block.querySelector("pre code, pre.recovered-data__value");
    return code ? code.textContent : null;
  }

  function setCopied(button, copied) {
    if (copied) {
      button.classList.add("copy-btn--copied");
      button.setAttribute("aria-label", COPIED_LABEL);
    } else {
      button.classList.remove("copy-btn--copied");
      button.setAttribute("aria-label", DEFAULT_LABEL);
    }
  }

  document.querySelectorAll(".copy-btn").forEach(function (button) {
    if (!button.getAttribute("aria-label")) {
      button.setAttribute("aria-label", DEFAULT_LABEL);
    }
    button.addEventListener("click", function () {
      var text = getCopyTarget(button);
      if (!text) return;
      copyText(text).then(function () {
        setCopied(button, true);
        window.setTimeout(function () {
          setCopied(button, false);
        }, 2000);
      });
    });
  });
})();
