(function () {
  var STEPS = [
    "Contacting agency relay nodes…",
    "Negotiating ephemeral tunnel…",
    "Validating agent credentials…",
    "Sealing field transmission…",
  ];

  var DELAY_MIN_MS = 450;
  var DELAY_MAX_MS = 750;

  var COMPLETED_URL = "mission-detail-completed.html";

  /* Hard-coded mock responses (production: POST /agent/api/missions/<slug>/submit JSON, outcome keys match 06-agent-experience.md). success-unlocks is a mock-only branch for non-empty new_missions. */
  var OUTCOMES = {
    success: {
      title: "Transmission accepted",
      body:
        "Lab verification confirmed your field data. This mission is now marked complete in the archive.",
      missions: [],
      redirect: COMPLETED_URL,
    },
    "success-unlocks": {
      title: "Transmission accepted",
      body:
        "Lab verification confirmed your field data. This mission is complete. The following mission(s) are now on your roster:",
      missions: [
        {
          title: "Training: Identify the Traitor",
          slug: "identify-the-traitor",
          group_name: "220.2 DevOps",
        },
      ],
      redirect: COMPLETED_URL,
    },
    invalid: {
      title: "Verification failed",
      body:
        "Analysts at the lab reviewed your transmission—the recovered data does not match mission parameters. Continue your fieldwork and submit again when you have the correct value.",
      missions: [],
    },
    not_yet: {
      title: "Not cleared for this channel",
      body:
        "Other agents are operating in parallel—we don't know who's who, and you mustn't either. Sharing intel is a good way to compromise the grid. Your mission trajectory doesn't allow you to complete this operation yet.",
      missions: [],
    },
  };

  var modal = document.getElementById("transmission-modal");
  if (!modal) return;

  var progressPanel = document.getElementById("transmission-progress");
  var outcomePanel = document.getElementById("transmission-outcome");
  var stepEl = document.getElementById("transmission-step");
  var barFill = document.getElementById("transmission-bar-fill");
  var outcomeTitle = document.getElementById("transmission-outcome-title");
  var outcomeBody = document.getElementById("transmission-outcome-body");
  var outcomeMissions = document.getElementById("transmission-outcome-missions");
  var okBtn = document.getElementById("transmission-ok");
  var form = document.getElementById("completion-form");
  var outcomeInput = document.getElementById("demo-outcome");

  var running = false;
  var currentOutcome = "invalid";

  function randomDelay() {
    return (
      Math.floor(Math.random() * (DELAY_MAX_MS - DELAY_MIN_MS + 1)) + DELAY_MIN_MS
    );
  }

  function wait(ms) {
    return new Promise(function (resolve) {
      window.setTimeout(resolve, ms);
    });
  }

  function openModal() {
    modal.hidden = false;
    document.body.classList.add("has-transmission-modal");
    okBtn.disabled = true;
  }

  function closeModal() {
    modal.hidden = true;
    document.body.classList.remove("has-transmission-modal");
    okBtn.disabled = false;
  }

  function showProgress() {
    progressPanel.hidden = false;
    outcomePanel.hidden = true;
    barFill.style.width = "0%";
  }

  function showOutcome(outcomeKey) {
    var data = OUTCOMES[outcomeKey] || OUTCOMES.invalid;
    currentOutcome = outcomeKey;
    outcomeTitle.textContent = data.title;
    outcomeBody.textContent = data.body;
    if (window.OutcomeMissions) {
      OutcomeMissions.render(outcomeMissions, data.missions);
    }
    progressPanel.hidden = true;
    outcomePanel.hidden = false;
    okBtn.disabled = false;
  }

  async function runTransmission(outcomeKey) {
    if (running) return;
    running = true;
    openModal();
    showProgress();

    for (var i = 0; i < STEPS.length; i++) {
      stepEl.textContent = STEPS[i];
      barFill.style.width = ((i + 1) / STEPS.length) * 100 + "%";
      await wait(randomDelay());
    }

    showOutcome(outcomeKey);
    running = false;
  }

  okBtn.addEventListener("click", function () {
    var data = OUTCOMES[currentOutcome];
    closeModal();
    if (data && data.redirect) {
      window.location.href = data.redirect;
    }
  });

  if (form) {
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      var key = (outcomeInput && outcomeInput.value) || "invalid";
      runTransmission(OUTCOMES[key] ? key : "invalid");
    });
  }

  document.querySelectorAll("[data-preview-outcome]").forEach(function (button) {
    button.addEventListener("click", function () {
      var key = button.getAttribute("data-preview-outcome");
      if (outcomeInput) outcomeInput.value = key;
      runTransmission(key);
    });
  });

  var params = new URLSearchParams(window.location.search);
  var queryOutcome = params.get("outcome");
  if (queryOutcome && OUTCOMES[queryOutcome] && outcomeInput) {
    outcomeInput.value = queryOutcome;
  }
})();
