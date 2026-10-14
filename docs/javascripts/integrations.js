/* The Integrations page's filters (how-to/integrations.md). Without this
   script the page shows its whole table and no filters. With it, the filters
   show; a row is shown when, in every group with a box ticked, it has one of
   the ticked values (AND across groups, OR within one), and the address's
   query keeps the choice: ?asset=fx&role=connectivity, a value repeated or
   comma-separated. Run on every page Material's instant navigation loads. */
(function () {
  var GROUPS = ["role", "asset", "environment"];

  function setUp() {
    var root = document.getElementById("om-integrations");
    if (!root || root.getAttribute("data-ready")) return;
    root.setAttribute("data-ready", "true");

    var form = root.querySelector(".om-integrations__filters");
    var rows = Array.prototype.slice.call(root.querySelectorAll("tbody tr"));
    var count = root.querySelector(".om-integrations__count");
    var empty = root.querySelector(".om-integrations__empty");
    var table = root.querySelector(".om-integrations__table");
    var boxes = Array.prototype.slice.call(form.querySelectorAll("input[type=checkbox]"));

    function chosen() {
      var choice = {};
      boxes.forEach(function (box) {
        if (box.checked) (choice[box.name] = choice[box.name] || []).push(box.value);
      });
      return choice;
    }

    function apply() {
      var choice = chosen();
      var shown = 0;
      rows.forEach(function (row) {
        var match = GROUPS.every(function (group) {
          var wanted = choice[group];
          if (!wanted) return true;
          var has = (row.getAttribute("data-" + group) || "").split(" ");
          return wanted.some(function (value) { return has.indexOf(value) !== -1; });
        });
        row.hidden = !match;
        if (match) shown += 1;
      });
      var filtered = Object.keys(choice).length > 0;
      count.textContent = filtered
        ? shown + " of " + rows.length + " plugins match"
        : rows.length + " plugins";
      empty.hidden = shown !== 0;
      table.hidden = shown === 0;

      var query = new URLSearchParams();
      GROUPS.forEach(function (group) {
        (choice[group] || []).forEach(function (value) { query.append(group, value); });
      });
      var search = query.toString();
      var url = location.pathname + (search ? "?" + search : "") + location.hash;
      if (url !== location.pathname + location.search + location.hash) {
        history.replaceState(history.state, "", url);
      }
    }

    var asked = new URLSearchParams(location.search);
    boxes.forEach(function (box) {
      var values = [];
      asked.getAll(box.name).forEach(function (value) {
        values = values.concat(value.toLowerCase().split(","));
      });
      box.checked = values.indexOf(box.value) !== -1;
    });

    form.addEventListener("change", apply);
    form.addEventListener("submit", function (event) { event.preventDefault(); });
    root.querySelector(".om-integrations__clear").addEventListener("click", function () {
      boxes.forEach(function (box) { box.checked = false; });
      apply();
    });
    form.hidden = false;
    apply();
  }

  if (typeof document$ !== "undefined") {
    document$.subscribe(setUp);
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", setUp);
  } else {
    setUp();
  }
})();
