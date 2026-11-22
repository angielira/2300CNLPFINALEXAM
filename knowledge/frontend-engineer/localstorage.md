# localStorage

- `setItem`, `getItem`, `removeItem`, `clear`; values are strings (use JSON).
- Persists across sessions with no expiry; scoped per origin (scheme + host + port).
- Private browsing data is cleared when the last private tab closes.
- Can throw `SecurityError` (blocked) or quota errors: wrap in try/catch.

## Sources
- https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage
