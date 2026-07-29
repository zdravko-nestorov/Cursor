---
name: profile-cache-header
overview: Add a 5-minute sessionStorage cache for userinfo and switch Profile Data to a header-only layout like the SCA page.
todos:
  - id: add-cache-util
    content: Add sessionStorage cache helper for user profile (5 min TTL).
    status: completed
  - id: use-cache-on-pages
    content: Use cache in Profile Menu/Profile/Profile Data load flow.
    status: completed
  - id: profile-data-header
    content: Replace Profile Data UI with title+subtitle header and adjust styles.
    status: completed
isProject: false
---

# Profile cache + Profile Data header

## Scope

- Cache Auth0 userinfo in `sessionStorage` for 5 minutes and reuse it on Profile Menu, Profile, and Profile Data.
- Replace Profile Data content with a header-only section (title + subtitle).

## Changes

- Create a small cache utility to centralize TTL logic and storage keys.
- Update profile pages to read from cache first and fall back to the API call.
- Simplify Profile Data layout to match the SCA-style header.

## Plan

- Add a cache helper in `[client/src/utils/userProfileCacheUtil.ts](/Users/zdravko.nestorov/Workspace/private/auth0-playground/client/src/utils/userProfileCacheUtil.ts)` with:
  - `getCachedUserProfile()` → returns cached data when `Date.now() - cachedAt < 5 * 60 * 1000`
  - `setCachedUserProfile(profile)` → stores `{ profile, cachedAt }` in `sessionStorage`
  - `clearCachedUserProfile()` → optional cleanup when auth fails
- Update `loadUserProfile()` in:
  - `[client/src/pages/ProfileMenuPage.tsx](/Users/zdravko.nestorov/Workspace/private/auth0-playground/client/src/pages/ProfileMenuPage.tsx)`
  - `[client/src/pages/ProfilePage.tsx](/Users/zdravko.nestorov/Workspace/private/auth0-playground/client/src/pages/ProfilePage.tsx)`
  - `[client/src/pages/ProfileDataPage.tsx](/Users/zdravko.nestorov/Workspace/private/auth0-playground/client/src/pages/ProfileDataPage.tsx)`
  to:
  - Check cache; if valid, set state and `isLoading=false` without calling `/api/userinfo`.
  - If cache invalid, fetch as today and `setCachedUserProfile(response.data)`.
  - On 401, navigate to login and clear cached profile.
- Replace Profile Data markup with a header-only section similar to SCA:
  - Keep back button and move it into the new header.
  - Render title + subtitle text: `Profile Data` and `Manage your personal information`.
  - Remove the profile info grid and avatar block.
- Add/adjust styles in `[client/src/styles/ProfileStyle.css](/Users/zdravko.nestorov/Workspace/private/auth0-playground/client/src/styles/ProfileStyle.css)` for the new header (mirroring the SCA header look but scoped to Profile Data).

## Notes

- Existing userinfo fetch happens in each page via `axios.get('/api/userinfo')`:

```
55:80:/Users/zdravko.nestorov/Workspace/private/auth0-playground/client/src/pages/ProfileMenuPage.tsx
  const loadUserProfile = async () => {
    try {
      await new Promise(resolve => setTimeout(resolve, 100));
      const accessToken = getAccessToken();
      ...
      const response = await axios.get('/api/userinfo', { headers: { Authorization: `Bearer ${accessToken}` } });
      setUserProfile(response.data);
      setIsLoading(false);
    } catch (err: any) { ... }
  };
```

## Verification

- Lint the modified TS/CSS files via `ReadLints`.
- Manually click Profile Menu → Profile / Profile Data within 5 minutes to confirm no repeat `/api/userinfo` calls and header-only UI on Profile Data.

