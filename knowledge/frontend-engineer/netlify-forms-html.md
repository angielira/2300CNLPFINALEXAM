# Netlify Forms in HTML

- Add `data-netlify="true"` (or `netlify`) and a unique `name` to the `<form>`; enable form detection in the Netlify UI.
- Netlify injects a hidden `form-name` input at deploy; include it yourself for AJAX or JS-rendered forms.
- AJAX: `fetch("/", {method: "POST", headers: {"Content-Type": "application/x-www-form-urlencoded"}, body: new URLSearchParams(formData).toString()})`. JSON is not supported.
- JS-rendered forms need a hidden static HTML copy with matching field names.

## Sources
- https://docs.netlify.com/manage/forms/setup
