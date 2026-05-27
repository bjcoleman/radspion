(function () {
  var STEPS = [
    "Contacting agency relay nodes…",
    "Negotiating ephemeral tunnel…",
    "Validating agent credentials…",
    "Sealing field transmission…",
  ];

  var DELAY_MIN_MS = 450;
  var DELAY_MAX_MS = 750;

  /* Hard-coded mock responses (production: POST /agent/api/unlock JSON, outcome keys match 06-agent-experience.md) */
  var OUTCOMES = {
    success: {
      title: "Mission added to roster",
      body: "Your unlock code was accepted. The following mission is now on your roster:",
      missions: [
        {
          title: "Training: Confidential Briefing",
          slug: "global-hidden",
          group_name: "Orientation",
        },
      ],
      addToRoster: true,
    },
    invalid: {
      title: "Verification failed",
      body:
        "Analysts could not validate that unlock code against agency records. Check the code and try again.",
      missions: [],
    },
    not_cleared: {
      title: "Not cleared for this channel",
      body:
        "That code is not issued for your clearance profile. Other agents may hold different access—you will not see their missions until your trajectory permits.",
      missions: [],
    },
  };

  var modal = document.getElementById("unlock-modal");
  if (!modal) return;

  var progressPanel = document.getElementById("unlock-progress");
  var outcomePanel = document.getElementById("unlock-outcome");
  var stepEl = document.getElementById("unlock-step");
  var barFill = document.getElementById("unlock-bar-fill");
  var outcomeTitle = document.getElementById("unlock-outcome-title");
  var outcomeBody = document.getElementById("unlock-outcome-body");
  var outcomeMissions = document.getElementById("unlock-outcome-missions");
  var okBtn = document.getElementById("unlock-ok");
  var form = document.getElementById("unlock-form");
  var codeInput = document.getElementById("unlock-code");
  var outcomeInput = document.getElementById("unlock-demo-outcome");

  var running = false;
  var pendingRosterUpdate = null;

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

  function resolveOutcomeKey() {
    var key = (outcomeInput && outcomeInput.value) || "invalid";
    return OUTCOMES[key] ? key : "invalid";
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
    pendingRosterUpdate = null;
  }

  function showOutcome(outcomeKey) {
    var data = OUTCOMES[outcomeKey] || OUTCOMES.invalid;
    outcomeTitle.textContent = data.title;
    outcomeBody.textContent = data.body;
    if (window.OutcomeMissions) {
      OutcomeMissions.render(outcomeMissions, data.missions);
    }
    if (data.addToRoster && data.missions && data.missions[0]) {
      pendingRosterUpdate = data.missions[0];
    }
    progressPanel.hidden = true;
    outcomePanel.hidden = false;
    okBtn.disabled = false;
  }

  function addMissionToRoster(mission) {
    var list = document.getElementById("orientation-mission-list");
    if (!list || list.querySelector('[data-slug="global-hidden"]')) return;

    var li = document.createElement("li");
    li.className = "mission-list__item";
    li.innerHTML =
      '<a class="mission-card mission-card--active" href="mission-detail-active.html" data-slug="' +
      mission.slug +
      '" data-status="active">' +
      '<span class="mission-card__body">' +
      '<span class="mission-card__title">' +
      mission.title +
      "</span>" +
      '<span class="mission-card__slug text-mono">' +
      mission.slug +
      "</span>" +
      '<span class="status-badge status-badge--active">active</span>' +
      "</span>" +
      '<span class="mission-card__arrow" aria-hidden="true">→</span>' +
      "</a>";
    list.insertBefore(li, list.firstChild);
  }

  async function runUnlock(outcomeKey) {
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
    if (pendingRosterUpdate) {
      addMissionToRoster(pendingRosterUpdate);
      pendingRosterUpdate = null;
    }
    closeModal();
    if (codeInput) codeInput.value = "";
    if (outcomeInput) outcomeInput.value = "";
  });

  if (form) {
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      runUnlock(resolveOutcomeKey());
    });
  }

  document.querySelectorAll("[data-unlock-preview]").forEach(function (button) {
    button.addEventListener("click", function () {
      var key = button.getAttribute("data-unlock-preview");
      if (outcomeInput) outcomeInput.value = key;
      runUnlock(key);
    });
  });

  var params = new URLSearchParams(window.location.search);
  var queryUnlock = params.get("unlock");
  if (queryUnlock && OUTCOMES[queryUnlock] && outcomeInput) {
    outcomeInput.value = queryUnlock;
  }
})();
