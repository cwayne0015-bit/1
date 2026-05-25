/* Unit tests for the CreatorsOS calculators.
 * Run:  node --test assets/js/   (Node 18+, no dependencies) */
const test = require("node:test");
const assert = require("node:assert/strict");
const os = require("./creatoros.js");

test("revenuePlan: basic sales math, no fees", () => {
  const r = os.revenuePlan(1000, 50, 0, 0);
  assert.equal(r.salesPerMonth, 20); // 1000 / 50
  assert.equal(r.netPerSale, 50);
  assert.equal(r.grossPerMonth, 1000);
  assert.equal(r.salesPerDay, round2(20 / 30));
  assert.equal(r.visitorsPerMonth, undefined); // conv = 0 -> traffic omitted
});

test("revenuePlan: fees reduce net and raise sales needed", () => {
  const r = os.revenuePlan(1000, 50, 0, 10); // net $45/sale
  assert.equal(r.netPerSale, 45);
  assert.equal(r.salesPerMonth, Math.ceil(1000 / 45)); // 23
});

test("revenuePlan: conversion rate yields traffic targets", () => {
  const r = os.revenuePlan(900, 30, 3, 0); // 30 sales, 3% conv
  assert.equal(r.salesPerMonth, 30);
  assert.equal(r.visitorsPerMonth, Math.ceil(30 / 0.03)); // 1000
  assert.equal(r.visitorsPerDay, Math.ceil(1000 / 30));
});

test("revenuePlan: rejects non-positive inputs", () => {
  assert.equal(os.revenuePlan(0, 50, 2, 0), null);
  assert.equal(os.revenuePlan(1000, 0, 2, 0), null);
  assert.equal(os.revenuePlan(1000, 50, 2, 100), null); // 100% fee -> net 0
});

test("smartPrice: driven by profit target", () => {
  const r = os.smartPrice(0, 0, 0, 1000, 40, 0); // need $1000 from 40 sales
  assert.equal(r.drivenBy, "goal");
  assert.equal(r.recommendedPrice, os.roundPrice(25)); // 1000/40 = 25
  assert.ok(r.monthlyProfit >= 1000 - 1); // meets target (within charm rounding)
});

test("smartPrice: floor lifts price when target is tiny", () => {
  // big investment, low target -> floor (recoup in 6 mo) wins
  const r = os.smartPrice(100, 50, 0, 10, 10, 0); // investment $5000
  assert.equal(r.investment, 5000);
  assert.equal(r.drivenBy, "floor");
  // floor price = 5000 / (6*10) = 83.33 -> charm
  assert.equal(r.floorPrice, os.roundPrice(5000 / 60));
  assert.ok(r.recommendedPrice >= r.floorPrice - 0.011);
});

test("smartPrice: fees are grossed up into the price", () => {
  const noFee = os.smartPrice(0, 0, 0, 1000, 50, 0);
  const fee = os.smartPrice(0, 0, 0, 1000, 50, 20);
  assert.ok(fee.recommendedPrice > noFee.recommendedPrice);
  assert.ok(fee.monthlyProfit >= 1000 - 1);
});

test("smartPrice: rejects non-positive sales/target", () => {
  assert.equal(os.smartPrice(1, 1, 1, 1000, 0, 0), null);
  assert.equal(os.smartPrice(1, 1, 1, 0, 10, 0), null);
});

test("roundPrice: charm pricing, never undershoots", () => {
  assert.equal(os.roundPrice(43.2), 43.99);
  assert.equal(os.roundPrice(50), 49.99);
  assert.equal(os.roundPrice(3), 3);   // tiny prices stay whole
  assert.equal(os.roundPrice(0), 0);
  assert.ok(os.roundPrice(43.2) >= 43.2);
});

test("checklistProgress: percentage rounding", () => {
  assert.equal(os.checklistProgress(0, 0), 0);
  assert.equal(os.checklistProgress(12, 0), 0);
  assert.equal(os.checklistProgress(12, 12), 100);
  assert.equal(os.checklistProgress(12, 6), 50);
  assert.equal(os.checklistProgress(3, 1), 33);
});

function round2(n) { return Math.round(n * 100) / 100; }
