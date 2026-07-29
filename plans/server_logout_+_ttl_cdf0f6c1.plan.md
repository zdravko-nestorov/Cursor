---
name: Server Logout + TTL
overview: Update client logout to use the server logout endpoint and extend the user profile cache TTL to 10 minutes.
todos:
  - id: update-logout
    content: Switch client logout to POST /api/logout and redirect to logoutURL
    status: completed
  - id: update-ttl
    content: Change user profile cache TTL to 10 minutes
    status: completed
isProject: false
---

## Scope

- Adjust client-side logout to call server `POST /api/logout` and redirect using returned `logoutURL` instead of constructing the Auth0 URL locally.
- Update cached user profile TTL from 5 minutes to 10 minutes.

## Key files

- [client/src/components/HeaderComponent.tsx](client/src/components/HeaderComponent.tsx)
- [client/src/utils/userProfileCacheUtil.ts](client/src/utils/userProfileCacheUtil.ts)

## Steps

1. In `HeaderComponent`, replace local Auth0 logout URL construction with a call to `POST /api/logout` (send `idToken`), then set `window.location.href` to the returned `logoutURL`. Keep local token/cache clearing before the call as requested.
2. Update `USER_PROFILE_TTL_MS` to `10 * 60 * 1000` in `userProfileCacheUtil.ts`.
3. Verify no other logout flow references need adjustment (client only), and keep error handling consistent (add minimal handling if the server call fails).

