# Multi-key authorization source review

Reviewed 2026-10-21 for version 2.2.0. This is a read-only source review, not a live customer test.

- The vendor's [Orguser folder](https://www.postman.com/servicedeskplus/servicedesk-plus-api/folder/dowvo47/orguser) describes organization-wide users, Org admin access through the ESM directory, and the prerequisite of more than one instance. It does not establish that an instance SDAdmin credential can read organization-wide data.
- The vendor's [Get all orgusers operation](https://www.postman.com/servicedeskplus/servicedesk-plus-api/request/7qfshjw/get-all-orgusers) publishes `GET /api/v3/orgusers` with API-key authorization, pagination input and an explicit `PORTALID` header. The public search-index representation exposed this example during the review; a direct page fetch returned only its navigation shell. The example supplies a placeholder, not a universal context ID. The implementation retains the existing header contract and requires a verified context from the administrator.
- The vendor's [on-premises User API](https://www.manageengine.com/products/service-desk/sdpop-v3-api/admin/user.html) covers instance User operations. These remain separate from Orguser collection.

Implementation consequences: keep the existing endpoint allowlist; require a separately explicit global credential assignment and administrator-supplied request context in multi-key mode; collect Orguser only once; preserve the existing observed-multiple-instances prerequisite. No role is inferred from an operation-level 403. No automatic OrgAdmin permission grant, guessed portal ID, new discovery endpoint, or unsupported ESM-wide export is introduced.

The installed build, exact ESM context ID and effective permissions still require administrator verification. Directory discovery, successful authentication, instance module access and organization-wide access are independent evidence. Existing single-key behavior remains for compatibility; multi-key mode does not inherit its implicit global credential use.
