(function (global) {
  function renderNewMissions(container, missions) {
    if (!container) return;
    container.innerHTML = "";
    if (!missions || missions.length === 0) {
      container.hidden = true;
      return;
    }
    container.hidden = false;
    missions.forEach(function (m) {
      var li = document.createElement("li");
      li.className = "outcome-missions__item";
      li.innerHTML =
        '<span class="outcome-missions__title">' +
        escapeHtml(m.title) +
        "</span>" +
        '<span class="outcome-missions__slug text-mono">' +
        escapeHtml(m.slug) +
        "</span>" +
        '<span class="outcome-missions__clearance">Clearance Level: ' +
        escapeHtml(m.group_name) +
        "</span>";
      container.appendChild(li);
    });
  }

  function escapeHtml(text) {
    var div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  global.OutcomeMissions = { render: renderNewMissions };
})(typeof window !== "undefined" ? window : this);
