---
name: restore-profile-data
overview: Restore Profile Data content while keeping the header, and ensure cached userinfo is used for Profile and Profile Data with fetch fallback.
todos: []
isProject: false
---

# Restore Profile Data content

## Scope

- Populate Profile Data with the original info grid while keeping the SCA-style header.
- Keep cache-first behavior for Profile and Profile Data; fetch only when cache is missing or expired.

## Plan

- Update `[client/src/pages/ProfileDataPage.tsx](/Users/zdravko.nestorov/Workspace/private/auth0-playground/client/src/pages/ProfileDataPage.tsx)`:
  - Keep the `profile-data-header` block.
  - Re-add the previous info grid (`profile-info-grid`, `info-card`, `verified-badge`, etc.) below the header, using the same fields as before.
- Ensure the existing cache-first logic remains intact (already present):
  - `getCachedUserProfile()` first, then fetch `/api/userinfo` if needed, then `setCachedUserProfile()`.
- No changes needed to `ProfilePage.tsx` unless cache logic is missing (already in place).

## Verification

- `ReadLints` on `ProfileDataPage.tsx`.
- Manually open Profile and Profile Data to confirm data shows and API is skipped when cache is warm.

