# Netlify Forms submissions

- View in the site's Forms tab; verified submissions by default; spam view available; CSV export of verified submissions.
- The Netlify API lists verified/spam submissions and deletes submissions/forms: `GET https://api.netlify.com/api/v1/sites/{site_id}/submissions` (all forms) returns verified submissions.
- The API returns up to 100 records per page and supports pagination.
- Export and delete regularly if submissions contain personal data.

## Sources
- https://docs.netlify.com/manage/forms/submissions/
- https://www.netlify.com/blog/2021/12/17/handling-form-submissions-via-the-netlify-api/
- https://answers.netlify.com/t/what-are-the-limits-to-the-forms-api/4735
