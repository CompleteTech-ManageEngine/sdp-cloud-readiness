# Diagnostic credential recovery — 2.1.2

## Established defects

The submitted 2.1.1 command combined `--diagnose` with `--directory-key`, but its log
showed only the original key prompt and one HTTP attempt. Source inspection found
`if topology.outcome in STOP_OUTCOMES or env.settings.get("diagnose_only"): return topology`
ahead of the secondary-credential handling. This was a scanner defect, not user error.

The subsequent ordinary all-portal command did show two key prompts and two
HTTP 403 / SDP 4002 directory failures. It then advertised D again although the
resolver allowed only one such attempt. This was a stale-menu defect; rejecting
an extra D did not cause the preceding second denial.

## Patch scope

The resolver now handles an explicitly requested secondary directory credential
before leaving diagnostic mode. This is conditional on incomplete initial
nonterminal discovery. Authentication failure of the initial credential and
interrupt/time/request-budget stops are not permission-retry triggers.

Diagnostic mode never queries module inventories. It does not recover scope from
saved profiles, interactive lists or files and does not save a new profile. It
still publishes sanitized diagnostics and the existing report family. Listed
portals in a successful diagnostic remain unassessed, not zero-record successes.

The secondary token can only be used on `/portals` with no PORTALID header.
The existing `DirectoryReader` routes through the initial client's rate limiter,
lock, budgets and redactor; it does not instantiate an independent allowance.
The original key remains the only credential used for later module reads.

Once the secondary attempt has run, the recovery menu offers L/F/Enter.
An additional D is explained without another key prompt or HTTP request.
Blank input with no known IDs explicitly finishes with diagnostics only.
This retains the existing bounded prompt loop; it does not trap unattended input.

## What is NOT repaired or inferred

The installed server's 403 denial is not fixed by these prompt/control-flow
changes. The second supplied key's identity, role membership and equality to the
initial key cannot be inferred from the sanitized console output. No ESM role
change, source upgrade, disabling of certificate verification, portal-ID range,
undocumented endpoint, session cookie or permission bypass is recommended.

Public research rechecked October 14, 2026 did not establish a ManageEngine
build-15240 guarantee or alternative authorized discovery API. The existing
`/portals` operation is described by Netskope for its integration; that is not a
universal on-premises contract. Use a vendor-confirmed read or a complete verified
scope to continue all selected portals in one run.

The available evidence is already sufficient to report the two-credential denial.
There is no need to repeat a full assessment or provide real keys to validate this patch.
