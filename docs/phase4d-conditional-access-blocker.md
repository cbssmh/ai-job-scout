# Phase 4D Conditional Access Blocker

Status: **Paused**
Recorded: 2026-09-26

## Blocker

Microsoft Entra denies operator authentication with `AADSTS53003` because
Conditional Access does not accept the current device state.

## Flows tested

- `ai-job-scout-operator-client`: secretless Device Code flow
- Microsoft Intune Web Company Portal: authorization-code flow
- Microsoft My Sign-Ins: Authorization Code + PKCE

All three flows were denied with `AADSTS53003`. This proves the blocker is not
limited to Device Code.

## Device evidence

Current Mac:

- macOS 26.7 on Apple Silicon
- not DEP-enrolled
- not MDM-enrolled
- Intune Company Portal not installed
- no Platform SSO device, login, or user configuration
- reported by Entra as macOS, device identifier unavailable, and unregistered

Current Entra/Intune inventory for the operator:

- one Windows workplace-registered device
- managed: yes
- compliant: no
- last observed sign-in: 2025-06-22
- no registered or compliant Mac
- no compliant device currently visible
- operator has active Intune Education and Entra ID Premium service plans

## Proven

- Conditional Access blocks authentication from this unregistered Mac.
- Device Code is not the sole cause because a PKCE flow fails identically.
- No currently visible operator device is compliant.
- This Mac is not presently enrolled or able to provide trusted device identity.

## Strongly evidenced

- A device-bound trust requirement is the active prerequisite because Entra
  reports the Mac as unregistered across Device Code, authorization-code, and
  PKCE attempts.
- Changing from Device Code to PKCE before establishing trusted device state
  would not resolve the observed blocker.
- Registration, compliance, or both are likely required before operator
  authentication can succeed from this Mac.

## Not proven

- The exact Conditional Access policy name.
- Whether its precise grant control requires registration, compliance, or both.
- Whether an additional approved-client, MFA, authentication-flow, device-filter,
  or other grant control also applies.
- Whether tenant enrollment restrictions currently permit this Mac to complete
  native Company Portal enrollment.

The operator account cannot read Conditional Access policy evaluation or sign-in
log details needed to resolve those points.

## Correlation IDs

- Device Code: `6f30e8af-1ceb-4d55-b195-69519d1aa443`
- Intune Web Company Portal: `3e3069e9-334d-4998-8c11-76b5e2e30b57`
- My Sign-Ins PKCE: `49af128a-9330-4945-bf09-9854f2f45001`

These non-secret identifiers are retained only to locate the corresponding
sign-in events during authorized operational troubleshooting.

## Approved resume condition

Resume Phase 4D only after operator authentication succeeds from a
registered/compliant device.

Until then, do not configure Easy Auth, assign application roles, deploy
authorization code, or modify tenant Conditional Access policy.
This blocker record does not recommend weakening or bypassing Conditional
Access.
