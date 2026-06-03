/**
 * Secure transmission modal — progress animation + outcome panel.
 *
 * RadspionTransmission.transmitSerialized({
 *   request: () => fetch(...).then(r => r.json()),
 *   renderOutcome: (data, outcomeEl) => { ... },
 *   redirectOnSuccess: true,
 *   onSuccess: (data) => { window.location.assign(...); },
 * });
 */
(function (global) {
  "use strict";

  const PRESET = {
    SUBMIT_DATA: "submitData",
  };

  const PRESETS = {
    [PRESET.SUBMIT_DATA]: {
      title: "Secure transmission",
      introText: "Initializing secure transmission…",
      dataLabel: "field data",
    },
  };

  /** Target ~3s; each delay is jittered independently. */
  const TIMING = {
    introHoldMs: 800,
    stepMs: 500,
    tailMs: 400,
    finalizeMs: 220,
    jitterSpread: 0.18,
  };

  const STEP_WIDTHS = [22, 48, 72, 90];

  const SUBMIT_FORM_SELECTOR = ".data-submit-form";

  function prefersReducedMotion() {
    return global.matchMedia("(prefers-reduced-motion: reduce)").matches;
  }

  function jitter(ms) {
    const spread = TIMING.jitterSpread;
    const delta = ms * spread * (Math.random() * 2 - 1);
    return Math.max(0, Math.round(ms + delta));
  }

  function delay(ms) {
    return new Promise(function (resolve) {
      global.setTimeout(resolve, ms);
    });
  }

  function buildSteps(dataLabel) {
    return [
      { text: "Initiating secure connection…", width: STEP_WIDTHS[0] },
      { text: "Establishing agent identity…", width: STEP_WIDTHS[1] },
      { text: "Transferring " + dataLabel + "…", width: STEP_WIDTHS[2] },
      { text: "Checking agency records…", width: STEP_WIDTHS[3] },
    ];
  }

  function TransmissionModal(root) {
    this.root = root;
    this.progress = root.querySelector("[data-transmission-progress]");
    this.outcome = root.querySelector("[data-transmission-outcome]");
    this.heading = root.querySelector("[data-transmission-heading]");
    this.stepEl = root.querySelector("[data-transmission-step]");
    this.barEl = root.querySelector("[data-transmission-bar-fill]");
    this._busy = false;
    this._boundOk = this._onOkClick.bind(this);
    this._boundKeydown = this._onKeydown.bind(this);
    root.addEventListener("click", this._boundOk);
  }

  TransmissionModal.prototype._setPageFormsDisabled = function (disabled) {
    const forms = global.document.querySelectorAll(SUBMIT_FORM_SELECTOR);
    forms.forEach(function (form) {
      const controls = form.querySelectorAll("input, button, select, textarea");
      controls.forEach(function (el) {
        if (disabled) {
          if (!el.disabled) {
            el.disabled = true;
            el.setAttribute("data-transmission-modal-disabled", "");
          }
        } else if (el.hasAttribute("data-transmission-modal-disabled")) {
          el.disabled = false;
          el.removeAttribute("data-transmission-modal-disabled");
        }
      });
    });
  };

  TransmissionModal.prototype._onKeydown = function (event) {
    if (!this._busy || this.root.hidden || event.key !== "Enter") {
      return;
    }
    if (!this.outcome.hidden) {
      const ok = this.outcome.querySelector(".transmission-modal__ok");
      if (ok) {
        event.preventDefault();
        event.stopPropagation();
        ok.click();
      }
      return;
    }
    event.preventDefault();
    event.stopPropagation();
  };

  TransmissionModal.prototype._onOkClick = function (event) {
    if (!event.target.closest(".transmission-modal__ok")) {
      return;
    }
    this.close();
  };

  TransmissionModal.prototype._requireElements = function () {
    return Boolean(
      this.progress && this.outcome && this.heading && this.stepEl && this.barEl,
    );
  };

  TransmissionModal.prototype.open = function (introText) {
    if (!this._requireElements()) {
      return;
    }
    this._busy = true;
    this._setPageFormsDisabled(true);
    global.document.addEventListener("keydown", this._boundKeydown, true);
    this.root.hidden = false;
    global.document.body.classList.add("has-transmission-modal");
    this.progress.hidden = false;
    this.outcome.hidden = true;
    this.outcome.replaceChildren();
    this.barEl.style.width = "0%";
    if (introText) {
      this.stepEl.textContent = introText;
    }
  };

  TransmissionModal.prototype.close = function () {
    this.root.hidden = true;
    global.document.body.classList.remove("has-transmission-modal");
    global.document.removeEventListener("keydown", this._boundKeydown, true);
    this._setPageFormsDisabled(false);
    this._busy = false;
  };

  TransmissionModal.prototype._applyPreset = function (presetKey) {
    const preset = PRESETS[presetKey];
    if (!preset) {
      throw new Error("Unknown transmission preset: " + presetKey);
    }
    this.heading.textContent = preset.title;
    return preset;
  };

  TransmissionModal.prototype._showOutcome = function (renderOutcome, result) {
    this.progress.hidden = true;
    this.outcome.hidden = false;
    renderOutcome(result, this.outcome);
    const ok = this.outcome.querySelector(".transmission-modal__ok");
    if (ok) {
      ok.focus();
    }
  };

  TransmissionModal.prototype.runProgress = function (presetKey) {
    const self = this;
    const preset = this._applyPreset(presetKey);
    const steps = buildSteps(preset.dataLabel);

    return new Promise(function (resolve) {
      if (!self._requireElements()) {
        resolve();
        return;
      }

      if (prefersReducedMotion()) {
        resolve();
        return;
      }

      (async function () {
        await delay(jitter(TIMING.introHoldMs));

        for (let i = 0; i < steps.length; i += 1) {
          const step = steps[i];
          self.stepEl.textContent = step.text;
          self.barEl.style.width = step.width + "%";
          await delay(jitter(TIMING.stepMs));
        }

        await delay(jitter(TIMING.tailMs));
        self.barEl.style.width = "100%";
        await delay(TIMING.finalizeMs);
        resolve();
      })();
    });
  };

  TransmissionModal.prototype.presentOutcome = function (renderOutcome, result) {
    if (!renderOutcome) {
      return Promise.reject(new Error("presentOutcome requires renderOutcome"));
    }
    if (!this._requireElements() || this._busy) {
      return Promise.resolve(result);
    }

    this._applyPreset(PRESET.SUBMIT_DATA);
    this._busy = true;
    this._setPageFormsDisabled(true);
    global.document.addEventListener("keydown", this._boundKeydown, true);
    this.root.hidden = false;
    global.document.body.classList.add("has-transmission-modal");
    this._showOutcome(renderOutcome, result);
    return Promise.resolve(result);
  };

  /**
   * Run progress animation, then the request. On success with redirectOnSuccess,
   * close the modal and call onSuccess without showing an outcome panel.
   */
  TransmissionModal.prototype.transmitSerialized = function (options) {
    const requestFn = options.request;
    const renderOutcome = options.renderOutcome;
    const redirectOnSuccess = Boolean(options.redirectOnSuccess);
    const onSuccess = options.onSuccess;

    if (!requestFn || !renderOutcome) {
      return Promise.reject(
        new Error("transmitSerialized requires request and renderOutcome"),
      );
    }

    if (this._busy) {
      return Promise.resolve();
    }

    const preset = this._applyPreset(PRESET.SUBMIT_DATA);
    this.open(preset.introText);

    const self = this;
    return this.runProgress(PRESET.SUBMIT_DATA)
      .then(function () {
        return Promise.resolve().then(requestFn);
      })
      .then(function (result) {
        if (result.outcome === "success" && redirectOnSuccess) {
          self.close();
          if (onSuccess) {
            onSuccess(result);
          }
          return result;
        }
        self._showOutcome(renderOutcome, result);
        return result;
      });
  };

  let instance = null;

  function getModal(root) {
    const el =
      root || global.document.querySelector("[data-transmission-modal]");
    if (!el) {
      return null;
    }
    if (!instance || instance.root !== el) {
      instance = new TransmissionModal(el);
    }
    return instance;
  }

  function presentOutcome(options) {
    const modal = getModal();
    if (!modal) {
      return Promise.reject(new Error("Transmission modal markup not found"));
    }
    return modal.presentOutcome(options.renderOutcome, options.result);
  }

  function transmitSerialized(options) {
    const modal = getModal();
    if (!modal) {
      return Promise.reject(new Error("Transmission modal markup not found"));
    }
    return modal.transmitSerialized(options);
  }

  global.RadspionTransmission = {
    PRESET: PRESET,
    PRESETS: PRESETS,
    getModal: getModal,
    presentOutcome: presentOutcome,
    transmitSerialized: transmitSerialized,
  };
})(typeof window !== "undefined" ? window : globalThis);
