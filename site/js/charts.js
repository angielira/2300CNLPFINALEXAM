/* HelpMate charts (Vega). Small, dependency-free helpers that build accessible
   charts from plain data. Everything is built with DOM methods and textContent,
   so data from JSON can never inject HTML.
   Every chart is: marks + direct value labels + a one-sentence caption + a data table. */

const SVG_NS = "http://www.w3.org/2000/svg";

export function el(tag, attrs = {}, kids = []) {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v === null || v === undefined || v === false) continue;
    if (k === "text") n.textContent = v;
    else n.setAttribute(k, v === true ? "" : String(v));
  }
  for (const kid of [].concat(kids)) {
    if (kid === null || kid === undefined) continue;
    n.append(kid);
  }
  return n;
}

function svgEl(tag, attrs = {}, text) {
  const n = document.createElementNS(SVG_NS, tag);
  for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, String(v));
  if (text !== undefined) n.textContent = text;
  return n;
}

export const pct = (x) => `${Math.round(Number(x) * 100)}%`;
export const num1 = (x) => (Math.round(Number(x) * 10) / 10).toFixed(1);

/* Horizontal bar list (pure CSS bars from app.css). rows: [{label, value, display}] */
export function barList(rows, max, ariaLabel) {
  const top = max || Math.max(1, ...rows.map((r) => r.value));
  const ul = el("ul", { class: "bar-list", "aria-label": ariaLabel });
  for (const r of rows) {
    const width = Math.max(0, Math.min(100, (r.value / top) * 100));
    ul.append(
      el("li", { class: "bar-row" }, [
        el("span", { class: "bar__label", text: r.label }),
        el("span", { class: "bar__track", "aria-hidden": "true" }, [
          el("span", { class: "bar__fill", style: `--value:${width.toFixed(1)}` }),
        ]),
        el("span", { class: "bar__value", text: r.display ?? String(r.value) }),
      ])
    );
  }
  return ul;
}

/* Data table. headers: [string]; rows: [[cell,...]] first cell is the row header;
   numeric cells (typeof number or flagged via numCols) are right aligned. */
export function dataTable(caption, headers, rows, numCols = []) {
  const thead = el("thead", {}, [
    el("tr", {}, headers.map((h, i) =>
      el("th", { scope: "col", class: numCols.includes(i) ? "num" : null, text: h }))),
  ]);
  const tbody = el("tbody", {}, rows.map((r) =>
    el("tr", {}, r.map((c, i) =>
      i === 0
        ? el("th", { scope: "row", text: String(c) })
        : el("td", { class: numCols.includes(i) ? "num" : null, text: String(c) })))));
  return el("div", { class: "table-wrap" }, [
    el("table", { class: "data-table" }, [el("caption", { text: caption }), thead, tbody]),
  ]);
}

export function tableDetails(caption, headers, rows, numCols) {
  return el("details", { class: "chart-table" }, [
    el("summary", { text: "Show this as a table" }),
    dataTable(caption, headers, rows, numCols),
  ]);
}

/* A finished chart block: figure (marks + caption) and table fallback. */
export function chartBlock(host, { marks, caption, legend, table }) {
  host.replaceChildren();
  const fig = el("figure", { class: "chart" }, [marks, el("figcaption", { class: "chart__caption", text: caption })]);
  host.append(fig);
  if (legend) host.append(legend);
  if (table) host.append(tableDetails(table.caption, table.headers, table.rows, table.numCols));
}

export function emptyState(host, message, title) {
  host.replaceChildren(
    el("div", { class: "empty-state" }, [
      title ? el("p", { class: "notice__title", text: title }) : null,
      el("p", { class: "notice__text", text: message }),
    ])
  );
}

/* Line chart as inline SVG: average stars (0-5) by week, every point labelled. */
export function lineChart(points, { yMax = 5, yLabel = "Average stars (1 to 5)", xLabel = "Week", title, desc, id }) {
  const W = 640, H = 320, m = { l: 64, r: 24, t: 24, b: 64 };
  const iw = W - m.l - m.r, ih = H - m.t - m.b;
  const svg = svgEl("svg", { viewBox: `0 0 ${W} ${H}`, role: "img", "aria-labelledby": `${id}-t ${id}-d` });
  svg.append(svgEl("title", { id: `${id}-t` }, title), svgEl("desc", { id: `${id}-d` }, desc));
  const y = (v) => m.t + ih - (v / yMax) * ih;
  const x = (i) => m.l + (points.length === 1 ? iw / 2 : (i / (points.length - 1)) * iw);
  for (let v = 0; v <= yMax; v += 1) {
    svg.append(svgEl("line", { class: "grid-line", x1: m.l, x2: W - m.r, y1: y(v), y2: y(v) }));
    svg.append(svgEl("text", { x: m.l - 10, y: y(v) + 5, "text-anchor": "end", "font-size": 15 }, String(v)));
  }
  svg.append(svgEl("line", { x1: m.l, x2: W - m.r, y1: y(0), y2: y(0), stroke: "#14213D", "stroke-width": 2 }));
  svg.append(svgEl("text", { x: 16, y: m.t + ih / 2, "font-size": 15, "text-anchor": "middle",
    transform: `rotate(-90 16 ${m.t + ih / 2})` }, yLabel));
  svg.append(svgEl("text", { x: m.l + iw / 2, y: H - 8, "font-size": 15, "text-anchor": "middle" }, xLabel));
  if (points.length > 1) {
    svg.append(svgEl("polyline", { fill: "none", stroke: "#1D5FD0", "stroke-width": 3,
      points: points.map((p, i) => `${x(i)},${y(p.value)}`).join(" ") }));
  }
  points.forEach((p, i) => {
    svg.append(svgEl("circle", { cx: x(i), cy: y(p.value), r: 6, fill: "#fff", stroke: "#1D5FD0", "stroke-width": 3 }));
    svg.append(svgEl("text", { x: x(i), y: y(p.value) - 14, "text-anchor": "middle", "font-size": 15 }, num1(p.value)));
    svg.append(svgEl("text", { x: x(i), y: H - m.b + 22, "text-anchor": "middle", "font-size": 14 }, p.label));
  });
  return svg;
}

/* Confusion matrix as a real table with numbers in every cell and a stepped navy ramp
   (no red/green). The diagonal is also bold with a thick border, so it is not color alone. */
export function heatTable(labels, matrix, names) {
  const steps = [
    { max: 0, bg: "#FFFFFF", fg: "#14213D" },
    { max: 0.25, bg: "#D6DEF0", fg: "#14213D" },
    { max: 0.5, bg: "#A9B7DA", fg: "#14213D" },
    { max: 0.75, bg: "#3D4F7C", fg: "#FFFFFF" },
    { max: 1, bg: "#14213D", fg: "#FFFFFF" },
  ];
  const pick = (r) => (r <= 0 ? steps[0] : steps.slice(1).find((s) => r <= s.max) || steps[4]);
  const head = el("tr", {}, [
    el("th", { scope: "col", text: "Real topic (rows) / HelpMate's guess (columns)" }),
    ...labels.map((l) => el("th", { scope: "col", class: "num", text: names[l] || l })),
  ]);
  const body = matrix.map((row, i) => {
    const total = row.reduce((a, b) => a + b, 0) || 1;
    return el("tr", {}, [
      el("th", { scope: "row", text: names[labels[i]] || labels[i] }),
      ...row.map((v, j) => {
        const s = pick(v / total);
        return el("td", {
          class: "num heat__cell" + (i === j ? " heat__cell--diag" : ""),
          style: `background:${s.bg};color:${s.fg}`,
          text: String(v),
        });
      }),
    ]);
  });
  return el("div", { class: "table-wrap" }, [
    el("table", { class: "data-table heat" }, [
      el("caption", { text: "Confusion matrix: how many test questions of each real topic got each guess" }),
      el("thead", {}, [head]),
      el("tbody", {}, body),
    ]),
  ]);
}

export function legendList(items) {
  return el("ul", { class: "legend" }, items.map((it) =>
    el("li", { class: "legend__item" }, [el("span", { class: `legend__swatch legend__swatch--${it.n}`, "aria-hidden": "true" }), it.label])));
}
