/* CreatorsOS — client-side toolkit.
 * Pure calculation functions are exported for Node tests (creatoros.test.js);
 * the DOM wiring at the bottom only runs in a browser. No dependencies. */
(function () {
  "use strict";

  // ── helpers ───────────────────────────────────────────────────────────────
  function num(v, fallback) {
    var n = parseFloat(v);
    return isFinite(n) ? n : (fallback === undefined ? 0 : fallback);
  }
  function clampPct(p) {
    p = num(p);
    if (p < 0) return 0;
    if (p > 100) return 100;
    return p;
  }
  function round2(n) { return Math.round(n * 100) / 100; }

  // Round a recommended price up to a clean charm price (e.g. 43.2 -> 43.99),
  // never below the raw figure so the seller doesn't undershoot the target.
  function roundPrice(p) {
    if (p <= 0) return 0;
    var whole = Math.ceil(p);
    return whole < 5 ? whole : whole - 0.01;
  }

  // ── Revenue Goal Planner ────────────────────────────────────────────────────
  // goal  : desired monthly take-home ($, after fees)
  // price : price per sale ($)
  // conv  : visitor -> buyer conversion rate (%) — optional (0 = unknown)
  // fee   : payment/platform fee (%) taken off each sale
  function revenuePlan(goal, price, conv, fee) {
    goal = num(goal); price = num(price); conv = num(conv); fee = clampPct(fee);
    if (goal <= 0 || price <= 0) return null;
    var netPerSale = price * (1 - fee / 100);
    if (netPerSale <= 0) return null;

    var salesPerMonth = Math.ceil(goal / netPerSale);
    var out = {
      netPerSale: round2(netPerSale),
      grossPerMonth: round2(salesPerMonth * price),
      salesPerMonth: salesPerMonth,
      salesPerWeek: Math.ceil(salesPerMonth / (52 / 12)),
      salesPerDay: round2(salesPerMonth / 30)
    };
    if (conv > 0) {
      var visitorsPerMonth = Math.ceil(salesPerMonth / (conv / 100));
      out.visitorsPerMonth = visitorsPerMonth;
      out.visitorsPerDay = Math.ceil(visitorsPerMonth / 30);
    }
    return out;
  }

  // ── Smart Pricing Lab ───────────────────────────────────────────────────────
  // hours/rate/costs : effort + cash that went into building it
  // targetProfit     : monthly take-home you want from this product ($)
  // sales            : sales/month you realistically expect (#)
  // fee              : payment/platform fee (%)
  function smartPrice(hours, rate, costs, targetProfit, sales, fee) {
    hours = num(hours); rate = num(rate); costs = num(costs);
    targetProfit = num(targetProfit); sales = num(sales); fee = clampPct(fee);
    if (sales <= 0 || targetProfit <= 0) return null;

    var investment = hours * rate + costs;
    var feeFactor = 1 - fee / 100;
    if (feeFactor <= 0) return null;

    // Price that nets the target profit at the expected volume.
    var goalPrice = (targetProfit / sales) / feeFactor;
    // Floor: at minimum recoup the build investment within 6 months.
    var floorPrice = investment > 0 ? (investment / (6 * sales)) / feeFactor : 0;

    var recommended = roundPrice(Math.max(goalPrice, floorPrice));
    var netPerSale = recommended * feeFactor;
    return {
      investment: round2(investment),
      recommendedPrice: recommended,
      floorPrice: roundPrice(floorPrice),
      monthlyProfit: round2(netPerSale * sales),
      monthsToRecoup: investment > 0 ? Math.ceil(investment / (netPerSale * sales)) : 0,
      drivenBy: goalPrice >= floorPrice ? "goal" : "floor"
    };
  }

  // ── Launch Checklist ────────────────────────────────────────────────────────
  function checklistProgress(total, done) {
    total = num(total); done = num(done);
    if (total <= 0) return 0;
    return Math.round((done / total) * 100);
  }

  var CreatorsOS = {
    num: num,
    clampPct: clampPct,
    round2: round2,
    roundPrice: roundPrice,
    revenuePlan: revenuePlan,
    smartPrice: smartPrice,
    checklistProgress: checklistProgress
  };

  // Export for Node test runner.
  if (typeof module !== "undefined" && module.exports) {
    module.exports = CreatorsOS;
  }

  // ── DOM wiring (browser only) ───────────────────────────────────────────────
  if (typeof document === "undefined") return;

  function $(id) { return document.getElementById(id); }
  function val(id) { var el = $(id); return el ? el.value : ""; }
  function set(id, text) { var el = $(id); if (el) el.textContent = text; }

  function money(n) {
    return "$" + Number(n).toLocaleString(undefined, {
      minimumFractionDigits: (n % 1 === 0 ? 0 : 2),
      maximumFractionDigits: 2
    });
  }
  function int(n) { return Number(Math.round(n)).toLocaleString(); }

  function bindInputs(ids, handler) {
    ids.forEach(function (id) {
      var el = $(id);
      if (el) el.addEventListener("input", handler);
    });
  }

  // Revenue Goal Planner
  function wireRevenue() {
    if (!$("rp-goal")) return;
    var ids = ["rp-goal", "rp-price", "rp-conv", "rp-fee"];
    function render() {
      var r = revenuePlan(val("rp-goal"), val("rp-price"), val("rp-conv"), val("rp-fee"));
      var out = $("rp-out"), hint = $("rp-hint");
      if (!r) {
        if (out) out.hidden = true;
        if (hint) hint.hidden = false;
        return;
      }
      if (hint) hint.hidden = true;
      if (out) out.hidden = false;
      set("rp-sales-month", int(r.salesPerMonth));
      set("rp-sales-week", int(r.salesPerWeek));
      set("rp-sales-day", r.salesPerDay);
      set("rp-net", money(r.netPerSale));
      set("rp-gross", money(r.grossPerMonth));
      var traffic = $("rp-traffic");
      if (traffic) {
        if (r.visitorsPerMonth != null) {
          traffic.hidden = false;
          set("rp-visitors-month", int(r.visitorsPerMonth));
          set("rp-visitors-day", int(r.visitorsPerDay));
        } else {
          traffic.hidden = true;
        }
      }
    }
    bindInputs(ids, render);
    render();
  }

  // Smart Pricing Lab
  function wirePricing() {
    if (!$("pl-sales")) return;
    var ids = ["pl-hours", "pl-rate", "pl-costs", "pl-profit", "pl-sales", "pl-fee"];
    function render() {
      var r = smartPrice(
        val("pl-hours"), val("pl-rate"), val("pl-costs"),
        val("pl-profit"), val("pl-sales"), val("pl-fee")
      );
      var out = $("pl-out"), hint = $("pl-hint");
      if (!r) {
        if (out) out.hidden = true;
        if (hint) hint.hidden = false;
        return;
      }
      if (hint) hint.hidden = true;
      if (out) out.hidden = false;
      set("pl-price", money(r.recommendedPrice));
      set("pl-floor", money(r.floorPrice));
      set("pl-investment", money(r.investment));
      set("pl-monthly", money(r.monthlyProfit));
      set("pl-recoup", r.monthsToRecoup > 0 ? r.monthsToRecoup + " mo" : "—");
      set("pl-note", r.drivenBy === "floor"
        ? "Set by your floor — at this volume a lower price wouldn't recoup the build in 6 months."
        : "Set by your profit target at the volume you entered.");
    }
    bindInputs(ids, render);
    render();
  }

  // Launch Checklist (state persisted in localStorage)
  function wireChecklist() {
    var root = $("checklist");
    if (!root) return;
    var KEY = "creatoros.checklist.v1";
    var boxes = Array.prototype.slice.call(root.querySelectorAll('input[type="checkbox"]'));
    var state = {};
    try { state = JSON.parse(localStorage.getItem(KEY) || "{}") || {}; } catch (e) { state = {}; }

    function save() {
      try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) {}
    }
    function render() {
      var done = boxes.filter(function (b) { return b.checked; }).length;
      var pct = checklistProgress(boxes.length, done);
      var bar = $("cl-bar");
      if (bar) bar.style.width = pct + "%";
      set("cl-pct", pct + "%");
      set("cl-count", done + " / " + boxes.length);
      var done2 = $("cl-done");
      if (done2) done2.hidden = pct < 100;
    }
    boxes.forEach(function (b) {
      var k = b.getAttribute("data-task");
      if (state[k]) b.checked = true;
      b.addEventListener("change", function () {
        state[k] = b.checked;
        save();
        render();
      });
    });
    var reset = $("cl-reset");
    if (reset) {
      reset.addEventListener("click", function () {
        state = {};
        save();
        boxes.forEach(function (b) { b.checked = false; });
        render();
      });
    }
    render();
  }

  document.addEventListener("DOMContentLoaded", function () {
    wireRevenue();
    wirePricing();
    wireChecklist();
  });
})();
