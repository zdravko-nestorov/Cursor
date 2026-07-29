---
name: sca-management-authenticators
overview: Add a backend SCA management authenticators API backed by Auth0 MFA, then wire the Security Details page to call it and display mapped authenticator data.
todos:
  - id: be-sca-service
    content: Add MFA authenticators service + endpoint + MFA jwtCheck.
    status: completed
  - id: fe-security-details
    content: Wire SecurityDetailsPage to call API and render list.
    status: completed
  - id: styles
    content: Style authenticator list/empty/error states.
    status: completed
  - id: verify
    content: Run lints + manual flow check.
    status: completed
isProject: false
---

# SCA Management Authenticators Plan

## Context

- New protected backend endpoint after `/api/wallet/transactions` that proxies Auth0 MFA authenticators using the SCA management access token.
- Frontend Security Details page should call that endpoint and render authenticators.

## Implementation Plan

### Backend

- Add a dedicated SCA management service to call Auth0 MFA authenticators and map the response.
  - Files: `[/Users/zdravko.nestorov/Workspace/private/auth0-playground/server/src/services/scaManagementService.ts](/Users/zdravko.nestorov/Workspace/private/auth0-playground/server/src/services/scaManagementService.ts)`, `[/Users/zdravko.nestorov/Workspace/private/auth0-playground/server/src/constants/auth0Constants.ts](/Users/zdravko.nestorov/Workspace/private/auth0-playground/server/src/constants/auth0Constants.ts)`
  - Add `AUTH0_ENDPOINTS.MFA_AUTHENTICATORS = ${AUTH0_CONFIG.TENANT_CUSTOM_DOMAIN}/mfa/authenticators`.
  - Implement `getScaAuthenticators(accessToken)` using axios GET with `Authorization: Bearer <sca_access_token>`.
  - Map response to a compact shape, e.g. `{ id, type, name, createdAt, lastAuthentication }`, defensively handling both array and `{ authenticators: [...] }` payloads.
- Add a new MFA-audience JWT middleware and endpoint.
  - Files: `[/Users/zdravko.nestorov/Workspace/private/auth0-playground/server/src/index.ts](/Users/zdravko.nestorov/Workspace/private/auth0-playground/server/src/index.ts)`
  - Create `jwtCheckMfa = auth({ audience: AUTH0_CONFIG.MFA_AUDIENCE, issuerBaseURL: AUTH0_CONFIG.TENANT_CUSTOM_DOMAIN })`.
  - Add `GET /api/wallet/sca/management/authenticators` after `/api/wallet/transactions`, using `jwtCheckMfa` and `getScaAuthenticators()`.
  - Extract access token from `Authorization` header (same as `/api/userinfo`).
  - Return mapped data and consistent error responses.
  - Update startup log list to include the new endpoint.

### Frontend

- Call the new endpoint with the SCA management access token and render the results.
  - Files: `[/Users/zdravko.nestorov/Workspace/private/auth0-playground/client/src/pages/SecurityDetailsPage.tsx](/Users/zdravko.nestorov/Workspace/private/auth0-playground/client/src/pages/SecurityDetailsPage.tsx)`
  - Add state for `authenticators`, `isLoadingAuthenticators`, and `authenticatorsError`.
  - After SCA management auth succeeds (token present), call `GET /api/wallet/sca/management/authenticators` with `Authorization: Bearer <sca_management_access_token>`.
  - On `401`, clear SCA management tokens and re-initiate the SCA management authorization flow.
  - Render a list (type/name/createdAt/lastAuthentication) and an empty state if none.
- Extend styles for the authenticator list and empty/error states.
  - Files: `[/Users/zdravko.nestorov/Workspace/private/auth0-playground/client/src/styles/SecurityDetailsStyle.css](/Users/zdravko.nestorov/Workspace/private/auth0-playground/client/src/styles/SecurityDetailsStyle.css)`

## Verification

- Lint check for modified files (ReadLints).
- Manual flow: login → Security Details → SCA management auth → see authenticators list or empty state.

