# Chart.js basics

- Put a `<canvas>` in its own wrapper `<div>`; load Chart.js from the jsDelivr CDN.
- `new Chart(ctx, {type: 'bar', data: {labels, datasets: [{label, data}]}, options: {scales: {y: {beginAtZero: true}}}})`.
- Canvas content isn't read by screen readers: add a text summary and a table fallback.

## Sources
- https://www.chartjs.org/docs/latest/getting-started/
- https://www.chartjs.org/docs/latest/general/accessibility.html
