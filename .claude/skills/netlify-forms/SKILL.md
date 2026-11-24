---
name: netlify-forms
description: "Collect HelpMate ratings with Netlify Forms and read them back at build time. Use for the rating form and feedback ingestion."
---

# netlify-forms

Used by: frontend-engineer, feedback-loop-engineer, netlify-engineer, security-reviewer

## Form
```html
<form name="rating" method="POST" data-netlify="true" netlify-honeypot="bot-field">
  <input type="hidden" name="form-name" value="rating">
  <p hidden><label>Don't fill: <input name="bot-field"></label></p>
  ...stars, comment, question, category, format...
</form>
```
- Enable **Forms -> Enable form detection** in Netlify; applies from the next deploy.
- AJAX: POST to `/` with `application/x-www-form-urlencoded` (not JSON).
- JS-rendered forms need a hidden static HTML copy with matching field names.
- Read back: `GET https://api.netlify.com/api/v1/sites/{site_id}/submissions` with a personal access token (env var), paginated.
