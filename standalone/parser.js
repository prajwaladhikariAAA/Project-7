/*
 * Browser-side statement parser — a JavaScript port of the Python
 * pdf_statement_converter parsing/verification logic, so the standalone HTML can
 * convert PDFs entirely client-side. Money is kept as integer cents for exactness.
 */
(function (root) {
  "use strict";

  // Matches "1,200.00", "$1,200.00", "(45.00)", "-45.00", "45.00 CR", etc.
  var AMOUNT_SRC = "\\(?\\s*[-+]?\\s*[$\u00a3\u20ac]?\\s*\\d[\\d,]*\\.\\d{2}\\s*\\)?(?:\\s*[CD]R)?";

  function parseAmountCents(token) {
    var text = String(token).trim();
    var negative = false;

    if (text.charAt(0) === "(" && text.replace(/\s+$/, "").slice(-1) === ")") {
      negative = true;
      text = text.trim().slice(1, -1);
    }

    var upper = text.toUpperCase().trim();
    if (upper.slice(-2) === "CR") {
      text = text.slice(0, upper.lastIndexOf("CR"));
    } else if (upper.slice(-2) === "DR") {
      negative = true;
      text = text.slice(0, upper.lastIndexOf("DR"));
    }

    text = text.replace(/,/g, "").replace(/[$\u00a3\u20ac]/g, "").trim();
    if (text.charAt(0) === "-") {
      negative = true;
      text = text.slice(1);
    } else if (text.charAt(0) === "+") {
      text = text.slice(1);
    }
    text = text.trim();

    var m = text.match(/^(\d+)\.(\d{2})$/);
    if (!m) throw new Error("Unparseable amount: " + token);
    var cents = parseInt(m[1], 10) * 100 + parseInt(m[2], 10);
    return negative ? -cents : cents;
  }

  var MONTHS = {
    jan: 1, feb: 2, mar: 3, apr: 4, may: 5, jun: 6,
    jul: 7, aug: 8, sep: 9, oct: 10, nov: 11, dec: 12,
  };

  function pad(n) {
    return (n < 10 ? "0" : "") + n;
  }

  function iso(y, mo, d) {
    if (mo < 1 || mo > 12 || d < 1 || d > 31) return null;
    return y + "-" + pad(mo) + "-" + pad(d);
  }

  function extractLeadingDate(line, dayfirst) {
    var s = line.replace(/^\s+/, "");
    var m;

    m = s.match(/^(\d{4})-(\d{1,2})-(\d{1,2})/);
    if (m) {
      var d1 = iso(+m[1], +m[2], +m[3]);
      if (d1) return { date: d1, rest: s.slice(m[0].length) };
    }

    m = s.match(/^(\d{1,2})[-\s]([A-Za-z]{3,9})[-\s](\d{2,4})/);
    if (m) {
      var mon = MONTHS[m[2].slice(0, 3).toLowerCase()];
      if (mon) {
        var y2 = +m[3];
        if (y2 < 100) y2 += 2000;
        var d2 = iso(y2, mon, +m[1]);
        if (d2) return { date: d2, rest: s.slice(m[0].length) };
      }
    }

    m = s.match(/^(\d{1,2})\/(\d{1,2})\/(\d{2,4})/);
    if (m) {
      var a = +m[1], b = +m[2], y3 = +m[3];
      if (y3 < 100) y3 += 2000;
      var mo, da;
      if (dayfirst) {
        da = a; mo = b;
        if (mo > 12) { mo = a; da = b; }
      } else {
        mo = a; da = b;
        if (mo > 12) { mo = b; da = a; }
      }
      var d3 = iso(y3, mo, da);
      if (d3) return { date: d3, rest: s.slice(m[0].length) };
    }

    return null;
  }

  function rowFromText(dateISO, text) {
    var matches = text.match(new RegExp(AMOUNT_SRC, "gi"));
    if (!matches) return null;
    var first = text.search(new RegExp(AMOUNT_SRC, "i"));
    var description = text.slice(0, first).trim();
    var amount, balance = null;
    try {
      amount = parseAmountCents(matches[0]);
      if (matches.length >= 2) balance = parseAmountCents(matches[matches.length - 1]);
    } catch (e) {
      return null;
    }
    return { date: dateISO, description: description, amount: amount, balance: balance };
  }

  var SUMMARY = [
    "total", "subtotal", "sub total", "opening balance", "closing balance",
    "balance brought forward", "balance carried forward", "brought forward",
    "carried forward", "statement", "page ", "continued",
  ];

  function looksSummary(text) {
    var low = text.trim().toLowerCase();
    for (var i = 0; i < SUMMARY.length; i++) {
      if (low.indexOf(SUMMARY[i]) === 0) return true;
    }
    return false;
  }

  function parseText(lines, opts) {
    opts = opts || {};
    var dayfirst = !!opts.dayfirst;
    var carry = opts.carryDate !== false;
    var rows = [];
    var last = null;
    for (var i = 0; i < lines.length; i++) {
      var line = lines[i];
      var found = extractLeadingDate(line, dayfirst);
      if (found) {
        last = found.date;
        var r1 = rowFromText(last, found.rest);
        if (r1) rows.push(r1);
      } else if (carry && last && !looksSummary(line)) {
        var r2 = rowFromText(last, line);
        if (r2) rows.push(r2);
      }
    }
    return rows;
  }

  function verifyBalances(rows, openingCents) {
    var running = (openingCents === undefined || openingCents === null) ? null : openingCents;
    var checked = 0;
    var disc = [];
    for (var i = 0; i < rows.length; i++) {
      var row = rows[i];
      if (running !== null) running += row.amount;
      if (row.balance === null) continue;
      if (running === null) { running = row.balance; continue; }
      checked++;
      if (running !== row.balance) {
        disc.push({
          index: i, date: row.date, description: row.description,
          amount: row.amount, expected: running, actual: row.balance,
          difference: row.balance - running,
        });
        running = row.balance;
      }
    }
    return { ok: disc.length === 0, checked: checked, discrepancies: disc };
  }

  function fmt(cents) {
    return (cents / 100).toFixed(2);
  }

  function csvEscape(v) {
    v = String(v);
    if (/[",\n]/.test(v)) return '"' + v.replace(/"/g, '""') + '"';
    return v;
  }

  function toCSV(rows, currency) {
    var out = ["date,description,amount,balance,currency"];
    for (var i = 0; i < rows.length; i++) {
      var r = rows[i];
      out.push([
        r.date, csvEscape(r.description), fmt(r.amount),
        r.balance === null ? "" : fmt(r.balance), currency,
      ].join(","));
    }
    return out.join("\r\n") + "\r\n";
  }

  var api = {
    parseAmountCents: parseAmountCents,
    extractLeadingDate: extractLeadingDate,
    rowFromText: rowFromText,
    parseText: parseText,
    verifyBalances: verifyBalances,
    toCSV: toCSV,
    fmt: fmt,
  };

  root.StatementParser = api;
  if (typeof module !== "undefined" && module.exports) module.exports = api;
})(typeof globalThis !== "undefined" ? globalThis : this);
