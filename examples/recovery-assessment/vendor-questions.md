# ServiceDesk Plus migration — portal-aware answers and confirmation questions

Generated: 2026-10-07T12:00:00+00:00

Each answer separates source evidence, API coverage, target unknowns, vendor commitments and project decisions. Source-only reads cannot prove future migration behavior.

### Q1 · Which documented limitations apply to our source environment and proposed target?

#### Confirmed source evidence

- Portal 1 (ID 1) / multiple: 5 affected records observed. An agreed historical-data disposition is required. \[portal:1:HISTORY\_WINDOW\_ONE\_YEAR\]
- Portal 1 (ID 1) / multiple: 1 affected records observed. An agreed historical-data disposition is required. \[portal:1:HISTORY\_WINDOW\_FIVE\_YEARS\]
- Portal 1 (ID 1) / requests: 1 affected records observed. The identified relationship requires a migration disposition. \[portal:1:LINKED\_REQUESTS\]
- Portal 1 (ID 1) / requests: 1 affected records observed. The identified relationship requires a migration disposition. \[portal:1:REQUEST\_DEPENDENCIES\]
- Portal 1 (ID 1) / requests: 1 affected records observed. The identified relationship requires a migration disposition. \[portal:1:REQUEST\_CHANGE\_LINKS\]
- Portal 1 (ID 1) / multiple: 1 observed owner totals exceed both interpretations of 48 MB. \[portal:1:ATTACHMENT\_SIZE\]
- Portal 1 (ID 1) / requests: 1 affected records observed. Identified note attachments require separate preservation. \[portal:1:NOTE\_ATTACHMENTS\]
- Portal 1 (ID 1) / technicians: 3 affected records observed. Resolve missing or shared technician email identities. \[portal:1:TECHNICIAN\_EMAILS\]
- Portal 1 (ID 1) / requests: 2 typed values checked; definitions, defaults, options, and uninspected record values may add exposure. \[portal:1:FIELD\_VALUE\_LENGTHS\]
- Portal 1 (ID 1) / requests: 1 affected records observed. The observed date ordering needs remediation. \[portal:1:REQUEST\_SCHEDULE\_DATES\]
- Portal 1 (ID 1) / computers: 2 affected records observed. Duplicate tags require a supported migration treatment. \[portal:1:DUPLICATE\_SERVICE\_TAGS\]
- Portal 1 (ID 1) / assets: 1 affected records observed. Observed date ordering can change migrated values. \[portal:1:ASSET\_DATE\_ORDER\]
- Portal 1 (ID 1) / multiple: 0 configuration objects and 4 record references observed. Source inventory does not verify target reconstruction. \[portal:1:WORKFLOW\_REBUILD\]
- Portal 1 (ID 1) / reports: 1 affected records observed. This query-report inventory may include built-ins; custom status and actual usage are not established. \[portal:1:QUERY\_REPORTS\]
- Portal 1 (ID 1) / templates: 2 templates exposed relevant nested metadata; 2 exceed a documented count limit. \[portal:1:TEMPLATE\_COMPLEXITY\]
- Portal 1 (ID 1) / requests: 1 resolution values measured; 1 exceed the documented limit. \[portal:1:RESOLUTION\_LENGTH\]
- Portal 1 (ID 1) / problems: 1 problems have observed ancillary content; unexposed problem configuration remains unassessed. \[portal:1:PROBLEM\_ANCILLARY\_DATA\]
- Portal 1 (ID 1) / requests: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:1:FIELD\_REQUESTS\_DEFAULT\_OPTION\_SIZE\]
- Portal 1 (ID 1) / requests: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:1:FIELD\_REQUESTS\_OPTION\_NORMALIZATION\]
- Portal 1 (ID 1) / changes: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:1:FIELD\_CHANGES\_DEFAULT\_OPTION\_SIZE\]
- Portal 1 (ID 1) / changes: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:1:FIELD\_CHANGES\_OPTION\_NORMALIZATION\]
- Portal 1 (ID 1) / assets: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:1:FIELD\_ASSETS\_DEFAULT\_OPTION\_SIZE\]
- Portal 1 (ID 1) / assets: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:1:FIELD\_ASSETS\_OPTION\_NORMALIZATION\]
- Portal 1 (ID 1) / computers: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:1:FIELD\_COMPUTERS\_DEFAULT\_OPTION\_SIZE\]
- Portal 1 (ID 1) / computers: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:1:FIELD\_COMPUTERS\_OPTION\_NORMALIZATION\]
- Portal 1 (ID 1) / cis: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:1:FIELD\_CIS\_DEFAULT\_OPTION\_SIZE\]
- Portal 1 (ID 1) / cis: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:1:FIELD\_CIS\_OPTION\_NORMALIZATION\]
- Portal 2 (ID 2) / multiple: 4 affected records observed. An agreed historical-data disposition is required. \[portal:2:HISTORY\_WINDOW\_ONE\_YEAR\]
- Portal 2 (ID 2) / multiple: 1 affected records observed. An agreed historical-data disposition is required. \[portal:2:HISTORY\_WINDOW\_FIVE\_YEARS\]
- Portal 2 (ID 2) / requests: 1 affected records observed. The identified relationship requires a migration disposition. \[portal:2:LINKED\_REQUESTS\]
- Portal 2 (ID 2) / requests: 1 affected records observed. The identified relationship requires a migration disposition. \[portal:2:REQUEST\_DEPENDENCIES\]
- Portal 2 (ID 2) / requests: 1 affected records observed. The identified relationship requires a migration disposition. \[portal:2:REQUEST\_CHANGE\_LINKS\]
- Portal 2 (ID 2) / multiple: 1 observed owner totals exceed both interpretations of 48 MB. \[portal:2:ATTACHMENT\_SIZE\]
- Portal 2 (ID 2) / requests: 1 affected records observed. Identified note attachments require separate preservation. \[portal:2:NOTE\_ATTACHMENTS\]
- Portal 2 (ID 2) / technicians: 3 affected records observed. Resolve missing or shared technician email identities. \[portal:2:TECHNICIAN\_EMAILS\]
- Portal 2 (ID 2) / requests: 2 typed values checked; definitions, defaults, options, and uninspected record values may add exposure. \[portal:2:FIELD\_VALUE\_LENGTHS\]
- Portal 2 (ID 2) / requests: 1 affected records observed. The observed date ordering needs remediation. \[portal:2:REQUEST\_SCHEDULE\_DATES\]
- Portal 2 (ID 2) / computers: 2 affected records observed. Duplicate tags require a supported migration treatment. \[portal:2:DUPLICATE\_SERVICE\_TAGS\]
- Portal 2 (ID 2) / assets: 1 affected records observed. Observed date ordering can change migrated values. \[portal:2:ASSET\_DATE\_ORDER\]
- Portal 2 (ID 2) / multiple: 0 configuration objects and 4 record references observed. Source inventory does not verify target reconstruction. \[portal:2:WORKFLOW\_REBUILD\]
- Portal 2 (ID 2) / reports: 1 affected records observed. This query-report inventory may include built-ins; custom status and actual usage are not established. \[portal:2:QUERY\_REPORTS\]
- Portal 2 (ID 2) / templates: 2 templates exposed relevant nested metadata; 2 exceed a documented count limit. \[portal:2:TEMPLATE\_COMPLEXITY\]
- Portal 2 (ID 2) / requests: 1 resolution values measured; 1 exceed the documented limit. \[portal:2:RESOLUTION\_LENGTH\]
- Portal 2 (ID 2) / problems: 1 problems have observed ancillary content; unexposed problem configuration remains unassessed. \[portal:2:PROBLEM\_ANCILLARY\_DATA\]
- Portal 2 (ID 2) / requests: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:2:FIELD\_REQUESTS\_DEFAULT\_OPTION\_SIZE\]
- Portal 2 (ID 2) / requests: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:2:FIELD\_REQUESTS\_OPTION\_NORMALIZATION\]
- Portal 2 (ID 2) / changes: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:2:FIELD\_CHANGES\_DEFAULT\_OPTION\_SIZE\]
- Portal 2 (ID 2) / changes: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:2:FIELD\_CHANGES\_OPTION\_NORMALIZATION\]
- Portal 2 (ID 2) / assets: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:2:FIELD\_ASSETS\_DEFAULT\_OPTION\_SIZE\]
- Portal 2 (ID 2) / assets: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:2:FIELD\_ASSETS\_OPTION\_NORMALIZATION\]
- Portal 2 (ID 2) / computers: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:2:FIELD\_COMPUTERS\_DEFAULT\_OPTION\_SIZE\]
- Portal 2 (ID 2) / computers: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:2:FIELD\_COMPUTERS\_OPTION\_NORMALIZATION\]
- Portal 3 (ID 3) / multiple: 4 affected records observed. An agreed historical-data disposition is required. \[portal:3:HISTORY\_WINDOW\_ONE\_YEAR\]
- Portal 3 (ID 3) / multiple: 1 affected records observed. An agreed historical-data disposition is required. \[portal:3:HISTORY\_WINDOW\_FIVE\_YEARS\]
- Portal 3 (ID 3) / requests: 1 affected records observed. The identified relationship requires a migration disposition. \[portal:3:LINKED\_REQUESTS\]
- Portal 3 (ID 3) / requests: 1 affected records observed. The identified relationship requires a migration disposition. \[portal:3:REQUEST\_DEPENDENCIES\]
- Portal 3 (ID 3) / requests: 1 affected records observed. The identified relationship requires a migration disposition. \[portal:3:REQUEST\_CHANGE\_LINKS\]
- Portal 3 (ID 3) / multiple: 1 observed owner totals exceed both interpretations of 48 MB. \[portal:3:ATTACHMENT\_SIZE\]
- Portal 3 (ID 3) / requests: 1 affected records observed. Identified note attachments require separate preservation. \[portal:3:NOTE\_ATTACHMENTS\]
- Portal 3 (ID 3) / technicians: 3 affected records observed. Resolve missing or shared technician email identities. \[portal:3:TECHNICIAN\_EMAILS\]
- Portal 3 (ID 3) / requests: 1 typed values checked; definitions, defaults, options, and uninspected record values may add exposure. \[portal:3:FIELD\_VALUE\_LENGTHS\]
- Portal 3 (ID 3) / requests: 1 affected records observed. The observed date ordering needs remediation. \[portal:3:REQUEST\_SCHEDULE\_DATES\]
- Portal 3 (ID 3) / assets: 1 affected records observed. Observed date ordering can change migrated values. \[portal:3:ASSET\_DATE\_ORDER\]
- Portal 3 (ID 3) / multiple: 0 configuration objects and 3 record references observed. Source inventory does not verify target reconstruction. \[portal:3:WORKFLOW\_REBUILD\]
- Portal 3 (ID 3) / reports: 1 affected records observed. This query-report inventory may include built-ins; custom status and actual usage are not established. \[portal:3:QUERY\_REPORTS\]
- Portal 3 (ID 3) / templates: 2 templates exposed relevant nested metadata; 2 exceed a documented count limit. \[portal:3:TEMPLATE\_COMPLEXITY\]
- Portal 3 (ID 3) / requests: 1 resolution values measured; 1 exceed the documented limit. \[portal:3:RESOLUTION\_LENGTH\]
- Portal 3 (ID 3) / problems: 1 problems have observed ancillary content; unexposed problem configuration remains unassessed. \[portal:3:PROBLEM\_ANCILLARY\_DATA\]
- Portal 3 (ID 3) / changes: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:3:FIELD\_CHANGES\_DEFAULT\_OPTION\_SIZE\]
- Portal 3 (ID 3) / changes: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:3:FIELD\_CHANGES\_OPTION\_NORMALIZATION\]
- Portal 3 (ID 3) / assets: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:3:FIELD\_ASSETS\_DEFAULT\_OPTION\_SIZE\]
- Portal 3 (ID 3) / assets: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:3:FIELD\_ASSETS\_OPTION\_NORMALIZATION\]
- Portal 3 (ID 3) / computers: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:3:FIELD\_COMPUTERS\_DEFAULT\_OPTION\_SIZE\]
- Portal 3 (ID 3) / computers: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:3:FIELD\_COMPUTERS\_OPTION\_NORMALIZATION\]

#### API coverage limitations

- Environment / topology: Portal discovery did not certify all API-visible topology.
- Portal 1 (ID 1) / technicians: COMPLETE Records observed: 3. List complete: true.
- Portal 1 (ID 1) / reports: COMPLETE Records observed: 1. List complete: true.
- Portal 1 (ID 1) / cmdb: COMPLETE Records observed: 1. List complete: true.
- Portal 1 (ID 1) / assets: COMPLETE Records observed: 3. List complete: true.
- Portal 1 (ID 1) / requests: COMPLETE Records observed: 3. List complete: true.
- Portal 1 (ID 1) / assets: COMPLETE Records observed: 2. List complete: true.
- Portal 1 (ID 1) / cmdb: COMPLETE Records observed: 2. List complete: true.
- Portal 1 (ID 1) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- Portal 1 (ID 1) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- Portal 2 (ID 2) / technicians: COMPLETE Records observed: 3. List complete: true.
- Portal 2 (ID 2) / reports: COMPLETE Records observed: 1. List complete: true.
- Portal 2 (ID 2) / cmdb: COMPLETE Records observed: 1. List complete: true.
- Portal 2 (ID 2) / projects: PERMISSION\_DENIED Records observed: —. List complete: false.
- Portal 2 (ID 2) / assets: COMPLETE Records observed: 2. List complete: true.
- Portal 2 (ID 2) / cmdb: COMPLETE Records observed: 2. List complete: true.
- Portal 2 (ID 2) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- Portal 2 (ID 2) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- Portal 3 (ID 3) / technicians: COMPLETE Records observed: 3. List complete: true.
- Portal 3 (ID 3) / reports: COMPLETE Records observed: 1. List complete: true.
- Portal 3 (ID 3) / cmdb: COMPLETE Records observed: 1. List complete: true.
- Portal 3 (ID 3) / assets: COMPLETE Records observed: 3. List complete: true.
- Portal 3 (ID 3) / releases: MODULE\_NOT\_AVAILABLE Records observed: —. List complete: false.
- Portal 3 (ID 3) / assets: COMPLETE Records observed: 1. List complete: true.
- Portal 3 (ID 3) / cmdb: COMPLETE Records observed: 2. List complete: true.
- Portal 4 (ID 4) / requests: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / requests: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / sites: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / groups: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / technicians: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / users: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / reports: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / cmdb: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / assets: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / requests: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / changes: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / problems: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / projects: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / releases: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / assets: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / assets: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / cmdb: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / contracts: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / purchases: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Environment / orgusers: COMPLETE Records observed: 2. List complete: true.
- Portal 1 (ID 1) / requests: 3 distinct additional fields observed; 3 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_REQUESTS\_COVERAGE\]
- Portal 1 (ID 1) / requests: 3 distinct additional fields observed; the documented total limit is 250. Target edition and per-type mapping still require confirmation. \[portal:1:FIELD\_REQUESTS\_CAPACITY\]
- Portal 1 (ID 1) / problems: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_PROBLEMS\_COVERAGE\]
- Portal 1 (ID 1) / problems: 1 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:1:FIELD\_PROBLEMS\_CAPACITY\]
- Portal 1 (ID 1) / changes: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_CHANGES\_COVERAGE\]
- Portal 1 (ID 1) / changes: 2 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:1:FIELD\_CHANGES\_CAPACITY\]
- Portal 1 (ID 1) / projects: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_PROJECTS\_COVERAGE\]
- Portal 1 (ID 1) / projects: 1 distinct additional fields observed; the documented total limit is 110. Target edition and per-type mapping still require confirmation. \[portal:1:FIELD\_PROJECTS\_CAPACITY\]
- Portal 1 (ID 1) / releases: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_RELEASES\_COVERAGE\]
- Portal 1 (ID 1) / releases: 1 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:1:FIELD\_RELEASES\_CAPACITY\]
- Portal 1 (ID 1) / users: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_USERS\_COVERAGE\]
- Portal 1 (ID 1) / users: 1 distinct additional fields observed; the documented total limit is 50. Target edition and per-type mapping still require confirmation. \[portal:1:FIELD\_USERS\_CAPACITY\]
- Portal 1 (ID 1) / technicians: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_TECHNICIANS\_COVERAGE\]
- Portal 1 (ID 1) / technicians: Additional-field count is unknown; the documented total limit is 50. Target edition and per-type mapping still require confirmation. \[portal:1:FIELD\_TECHNICIANS\_CAPACITY\]
- Portal 1 (ID 1) / assets: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_ASSETS\_COVERAGE\]
- Portal 1 (ID 1) / assets: 2 distinct additional fields observed; the documented total limit is 100. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. \[portal:1:FIELD\_ASSETS\_CAPACITY\]
- Portal 1 (ID 1) / computers: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_COMPUTERS\_COVERAGE\]
- Portal 1 (ID 1) / computers: 2 distinct additional fields observed; the documented total limit is 52. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. \[portal:1:FIELD\_COMPUTERS\_CAPACITY\]
- Portal 1 (ID 1) / cis: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_CIS\_COVERAGE\]
- Portal 1 (ID 1) / cis: 2 distinct additional fields observed; the documented total limit is 1560. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. \[portal:1:FIELD\_CIS\_CAPACITY\]
- Portal 1 (ID 1) / contracts: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_CONTRACTS\_COVERAGE\]
- Portal 1 (ID 1) / contracts: Additional-field count is unknown; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:1:FIELD\_CONTRACTS\_CAPACITY\]
- Portal 1 (ID 1) / purchases: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_PURCHASES\_COVERAGE\]
- Portal 1 (ID 1) / purchases: Additional-field count is unknown; the documented total limit is 164. Target edition and per-type mapping still require confirmation. \[portal:1:FIELD\_PURCHASES\_CAPACITY\]
- Portal 2 (ID 2) / requests: 3 distinct additional fields observed; 3 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_REQUESTS\_COVERAGE\]
- Portal 2 (ID 2) / requests: 3 distinct additional fields observed; the documented total limit is 250. Target edition and per-type mapping still require confirmation. \[portal:2:FIELD\_REQUESTS\_CAPACITY\]
- Portal 2 (ID 2) / problems: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_PROBLEMS\_COVERAGE\]
- Portal 2 (ID 2) / problems: 1 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:2:FIELD\_PROBLEMS\_CAPACITY\]
- Portal 2 (ID 2) / changes: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_CHANGES\_COVERAGE\]
- Portal 2 (ID 2) / changes: 2 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:2:FIELD\_CHANGES\_CAPACITY\]
- Portal 2 (ID 2) / projects: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_PROJECTS\_COVERAGE\]
- Portal 2 (ID 2) / projects: Additional-field count is unknown; the documented total limit is 110. Target edition and per-type mapping still require confirmation. \[portal:2:FIELD\_PROJECTS\_CAPACITY\]
- Portal 2 (ID 2) / releases: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_RELEASES\_COVERAGE\]
- Portal 2 (ID 2) / releases: 1 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:2:FIELD\_RELEASES\_CAPACITY\]
- Portal 2 (ID 2) / users: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_USERS\_COVERAGE\]
- Portal 2 (ID 2) / users: 1 distinct additional fields observed; the documented total limit is 50. Target edition and per-type mapping still require confirmation. \[portal:2:FIELD\_USERS\_CAPACITY\]
- Portal 2 (ID 2) / technicians: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_TECHNICIANS\_COVERAGE\]
- Portal 2 (ID 2) / technicians: Additional-field count is unknown; the documented total limit is 50. Target edition and per-type mapping still require confirmation. \[portal:2:FIELD\_TECHNICIANS\_CAPACITY\]
- Portal 2 (ID 2) / assets: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: PARTIAL. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_ASSETS\_COVERAGE\]
- Portal 2 (ID 2) / assets: 2 distinct additional fields observed; the documented total limit is 100. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. \[portal:2:FIELD\_ASSETS\_CAPACITY\]
- Portal 2 (ID 2) / computers: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_COMPUTERS\_COVERAGE\]
- Portal 2 (ID 2) / computers: 2 distinct additional fields observed; the documented total limit is 52. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. \[portal:2:FIELD\_COMPUTERS\_CAPACITY\]
- Portal 2 (ID 2) / cis: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_CIS\_COVERAGE\]
- Portal 2 (ID 2) / cis: 1 distinct additional fields observed; the documented total limit is 1560. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. \[portal:2:FIELD\_CIS\_CAPACITY\]
- Portal 2 (ID 2) / contracts: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_CONTRACTS\_COVERAGE\]
- Portal 2 (ID 2) / contracts: Additional-field count is unknown; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:2:FIELD\_CONTRACTS\_CAPACITY\]
- Portal 2 (ID 2) / purchases: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_PURCHASES\_COVERAGE\]
- Portal 2 (ID 2) / purchases: Additional-field count is unknown; the documented total limit is 164. Target edition and per-type mapping still require confirmation. \[portal:2:FIELD\_PURCHASES\_CAPACITY\]
- Portal 3 (ID 3) / requests: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_REQUESTS\_COVERAGE\]
- Portal 3 (ID 3) / requests: 1 distinct additional fields observed; the documented total limit is 250. Target edition and per-type mapping still require confirmation. \[portal:3:FIELD\_REQUESTS\_CAPACITY\]
- Portal 3 (ID 3) / problems: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_PROBLEMS\_COVERAGE\]
- Portal 3 (ID 3) / problems: 1 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:3:FIELD\_PROBLEMS\_CAPACITY\]
- Portal 3 (ID 3) / changes: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_CHANGES\_COVERAGE\]
- Portal 3 (ID 3) / changes: 2 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:3:FIELD\_CHANGES\_CAPACITY\]
- Portal 3 (ID 3) / projects: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_PROJECTS\_COVERAGE\]
- Portal 3 (ID 3) / projects: 1 distinct additional fields observed; the documented total limit is 110. Target edition and per-type mapping still require confirmation. \[portal:3:FIELD\_PROJECTS\_CAPACITY\]
- Portal 3 (ID 3) / releases: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_RELEASES\_COVERAGE\]
- Portal 3 (ID 3) / releases: Additional-field count is unknown; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:3:FIELD\_RELEASES\_CAPACITY\]
- Portal 3 (ID 3) / users: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_USERS\_COVERAGE\]
- Portal 3 (ID 3) / users: 1 distinct additional fields observed; the documented total limit is 50. Target edition and per-type mapping still require confirmation. \[portal:3:FIELD\_USERS\_CAPACITY\]
- Portal 3 (ID 3) / technicians: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_TECHNICIANS\_COVERAGE\]
- Portal 3 (ID 3) / technicians: Additional-field count is unknown; the documented total limit is 50. Target edition and per-type mapping still require confirmation. \[portal:3:FIELD\_TECHNICIANS\_CAPACITY\]
- Portal 3 (ID 3) / assets: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_ASSETS\_COVERAGE\]
- Portal 3 (ID 3) / assets: 2 distinct additional fields observed; the documented total limit is 100. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. \[portal:3:FIELD\_ASSETS\_CAPACITY\]
- Portal 3 (ID 3) / computers: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_COMPUTERS\_COVERAGE\]
- Portal 3 (ID 3) / computers: 2 distinct additional fields observed; the documented total limit is 52. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. \[portal:3:FIELD\_COMPUTERS\_CAPACITY\]
- Portal 3 (ID 3) / cis: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_CIS\_COVERAGE\]
- Portal 3 (ID 3) / cis: 1 distinct additional fields observed; the documented total limit is 1560. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. \[portal:3:FIELD\_CIS\_CAPACITY\]
- Portal 3 (ID 3) / contracts: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_CONTRACTS\_COVERAGE\]
- Portal 3 (ID 3) / contracts: Additional-field count is unknown; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:3:FIELD\_CONTRACTS\_CAPACITY\]
- Portal 3 (ID 3) / purchases: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_PURCHASES\_COVERAGE\]
- Portal 3 (ID 3) / purchases: Additional-field count is unknown; the documented total limit is 164. Target edition and per-type mapping still require confirmation. \[portal:3:FIELD\_PURCHASES\_CAPACITY\]
- Portal 4 (ID 4) / requests: 0 distinct request-field definitions observed; 0 have recognized types. The combined paid-tier limit is 250. \[portal:4:REQUEST\_FIELD\_CAPACITY\]
- Portal 4 (ID 4) / requests: No matching issue established from 0 checked records; collection or required-field coverage is incomplete. \[portal:4:FIELD\_NAME\_COLLISIONS\]
- Portal 4 (ID 4) / requests: 0 typed values checked; definitions, defaults, options, and uninspected record values may add exposure. \[portal:4:FIELD\_VALUE\_LENGTHS\]

#### Target-cloud unknowns

- Target build support, edition, datacenter and effective tenant limits have not been read.

#### Vendor confirmation required

- Confirm supported source builds and the mapping of every selected source portal to a target service desk.

#### Project/business decision required

- Confirm the intended target topology, required modules and acceptance criteria.

### Q2 · How should old records, CMDB, Releases, Projects and custom modules be handled?

#### Confirmed source evidence

- Portal 1 (ID 1) / multiple: 5 affected records observed. An agreed historical-data disposition is required. \[portal:1:HISTORY\_WINDOW\_ONE\_YEAR\]
- Portal 1 (ID 1) / multiple: 1 affected records observed. An agreed historical-data disposition is required. \[portal:1:HISTORY\_WINDOW\_FIVE\_YEARS\]
- Portal 1 (ID 1) / computers: 2 affected records observed. Duplicate tags require a supported migration treatment. \[portal:1:DUPLICATE\_SERVICE\_TAGS\]
- Portal 1 (ID 1) / assets: 1 affected records observed. Observed date ordering can change migrated values. \[portal:1:ASSET\_DATE\_ORDER\]
- Portal 1 (ID 1) / requests: 1 resolution values measured; 1 exceed the documented limit. \[portal:1:RESOLUTION\_LENGTH\]
- Portal 1 (ID 1) / problems: 1 problems have observed ancillary content; unexposed problem configuration remains unassessed. \[portal:1:PROBLEM\_ANCILLARY\_DATA\]
- Portal 2 (ID 2) / multiple: 4 affected records observed. An agreed historical-data disposition is required. \[portal:2:HISTORY\_WINDOW\_ONE\_YEAR\]
- Portal 2 (ID 2) / multiple: 1 affected records observed. An agreed historical-data disposition is required. \[portal:2:HISTORY\_WINDOW\_FIVE\_YEARS\]
- Portal 2 (ID 2) / computers: 2 affected records observed. Duplicate tags require a supported migration treatment. \[portal:2:DUPLICATE\_SERVICE\_TAGS\]
- Portal 2 (ID 2) / assets: 1 affected records observed. Observed date ordering can change migrated values. \[portal:2:ASSET\_DATE\_ORDER\]
- Portal 2 (ID 2) / requests: 1 resolution values measured; 1 exceed the documented limit. \[portal:2:RESOLUTION\_LENGTH\]
- Portal 2 (ID 2) / problems: 1 problems have observed ancillary content; unexposed problem configuration remains unassessed. \[portal:2:PROBLEM\_ANCILLARY\_DATA\]
- Portal 3 (ID 3) / multiple: 4 affected records observed. An agreed historical-data disposition is required. \[portal:3:HISTORY\_WINDOW\_ONE\_YEAR\]
- Portal 3 (ID 3) / multiple: 1 affected records observed. An agreed historical-data disposition is required. \[portal:3:HISTORY\_WINDOW\_FIVE\_YEARS\]
- Portal 3 (ID 3) / assets: 1 affected records observed. Observed date ordering can change migrated values. \[portal:3:ASSET\_DATE\_ORDER\]
- Portal 3 (ID 3) / requests: 1 resolution values measured; 1 exceed the documented limit. \[portal:3:RESOLUTION\_LENGTH\]
- Portal 3 (ID 3) / problems: 1 problems have observed ancillary content; unexposed problem configuration remains unassessed. \[portal:3:PROBLEM\_ANCILLARY\_DATA\]

#### API coverage limitations

- Environment / topology: Portal discovery did not certify all API-visible topology.
- Portal 1 (ID 1) / technicians: COMPLETE Records observed: 3. List complete: true.
- Portal 1 (ID 1) / reports: COMPLETE Records observed: 1. List complete: true.
- Portal 1 (ID 1) / cmdb: COMPLETE Records observed: 1. List complete: true.
- Portal 1 (ID 1) / assets: COMPLETE Records observed: 3. List complete: true.
- Portal 1 (ID 1) / requests: COMPLETE Records observed: 3. List complete: true.
- Portal 1 (ID 1) / assets: COMPLETE Records observed: 2. List complete: true.
- Portal 1 (ID 1) / cmdb: COMPLETE Records observed: 2. List complete: true.
- Portal 1 (ID 1) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- Portal 1 (ID 1) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- Portal 2 (ID 2) / technicians: COMPLETE Records observed: 3. List complete: true.
- Portal 2 (ID 2) / reports: COMPLETE Records observed: 1. List complete: true.
- Portal 2 (ID 2) / cmdb: COMPLETE Records observed: 1. List complete: true.
- Portal 2 (ID 2) / projects: PERMISSION\_DENIED Records observed: —. List complete: false.
- Portal 2 (ID 2) / assets: COMPLETE Records observed: 2. List complete: true.
- Portal 2 (ID 2) / cmdb: COMPLETE Records observed: 2. List complete: true.
- Portal 2 (ID 2) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- Portal 2 (ID 2) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- Portal 3 (ID 3) / technicians: COMPLETE Records observed: 3. List complete: true.
- Portal 3 (ID 3) / reports: COMPLETE Records observed: 1. List complete: true.
- Portal 3 (ID 3) / cmdb: COMPLETE Records observed: 1. List complete: true.
- Portal 3 (ID 3) / assets: COMPLETE Records observed: 3. List complete: true.
- Portal 3 (ID 3) / releases: MODULE\_NOT\_AVAILABLE Records observed: —. List complete: false.
- Portal 3 (ID 3) / assets: COMPLETE Records observed: 1. List complete: true.
- Portal 3 (ID 3) / cmdb: COMPLETE Records observed: 2. List complete: true.
- Portal 4 (ID 4) / requests: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / requests: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / sites: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / groups: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / technicians: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / users: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / reports: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / cmdb: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / assets: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / requests: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / changes: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / problems: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / projects: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / releases: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / assets: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / assets: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / cmdb: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / contracts: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / purchases: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Environment / orgusers: COMPLETE Records observed: 2. List complete: true.

#### Target-cloud unknowns

- The scan cannot verify target import coverage, historical-window exceptions or custom-module equivalence.

#### Vendor confirmation required

- Confirm supported migration or retention routes for each portal/module, age group, CMDB relationship and Release/Project subresource.

#### Project/business decision required

- Choose required history retention, source archive access and ownership of data that needs a separate route.

### Q3 · What needs confirmation regarding final-delta migration?

#### Confirmed source evidence

No applicable evidence established; absence or target compatibility is not certified.

#### API coverage limitations

- Environment / topology: Portal discovery did not certify all API-visible topology.
- Portal 1 (ID 1) / technicians: COMPLETE Records observed: 3. List complete: true.
- Portal 1 (ID 1) / reports: COMPLETE Records observed: 1. List complete: true.
- Portal 1 (ID 1) / cmdb: COMPLETE Records observed: 1. List complete: true.
- Portal 1 (ID 1) / assets: COMPLETE Records observed: 3. List complete: true.
- Portal 1 (ID 1) / requests: COMPLETE Records observed: 3. List complete: true.
- Portal 1 (ID 1) / assets: COMPLETE Records observed: 2. List complete: true.
- Portal 1 (ID 1) / cmdb: COMPLETE Records observed: 2. List complete: true.
- Portal 1 (ID 1) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- Portal 1 (ID 1) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- Portal 2 (ID 2) / technicians: COMPLETE Records observed: 3. List complete: true.
- Portal 2 (ID 2) / reports: COMPLETE Records observed: 1. List complete: true.
- Portal 2 (ID 2) / cmdb: COMPLETE Records observed: 1. List complete: true.
- Portal 2 (ID 2) / projects: PERMISSION\_DENIED Records observed: —. List complete: false.
- Portal 2 (ID 2) / assets: COMPLETE Records observed: 2. List complete: true.
- Portal 2 (ID 2) / cmdb: COMPLETE Records observed: 2. List complete: true.
- Portal 2 (ID 2) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- Portal 2 (ID 2) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- Portal 3 (ID 3) / technicians: COMPLETE Records observed: 3. List complete: true.
- Portal 3 (ID 3) / reports: COMPLETE Records observed: 1. List complete: true.
- Portal 3 (ID 3) / cmdb: COMPLETE Records observed: 1. List complete: true.
- Portal 3 (ID 3) / assets: COMPLETE Records observed: 3. List complete: true.
- Portal 3 (ID 3) / releases: MODULE\_NOT\_AVAILABLE Records observed: —. List complete: false.
- Portal 3 (ID 3) / assets: COMPLETE Records observed: 1. List complete: true.
- Portal 3 (ID 3) / cmdb: COMPLETE Records observed: 2. List complete: true.
- Portal 4 (ID 4) / requests: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / requests: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / sites: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / groups: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / technicians: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / users: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / reports: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / cmdb: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / assets: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / requests: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / changes: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / problems: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / projects: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / releases: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / assets: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / assets: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / cmdb: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / contracts: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / purchases: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Environment / orgusers: COMPLETE Records observed: 2. List complete: true.

#### Target-cloud unknowns

- Source reads cannot establish the future delta's handling of edits, deletes or newly added subentities.

#### Vendor confirmation required

- Confirm reconciliation of changed/deleted records, notes, attachments, approvals and tasks, plus target freshness and rollback behavior.

#### Project/business decision required

- Approve the freeze window, mail transition, delta rehearsal and rollback decision owner.

### Q4 · Which identifiers and relationships require preservation or cross-reference?

#### Confirmed source evidence

- Portal 1 (ID 1) / requests: 1 affected records observed. The identified relationship requires a migration disposition. \[portal:1:LINKED\_REQUESTS\]
- Portal 1 (ID 1) / requests: 1 affected records observed. The identified relationship requires a migration disposition. \[portal:1:REQUEST\_DEPENDENCIES\]
- Portal 1 (ID 1) / requests: 1 affected records observed. The identified relationship requires a migration disposition. \[portal:1:REQUEST\_CHANGE\_LINKS\]
- Portal 2 (ID 2) / requests: 1 affected records observed. The identified relationship requires a migration disposition. \[portal:2:LINKED\_REQUESTS\]
- Portal 2 (ID 2) / requests: 1 affected records observed. The identified relationship requires a migration disposition. \[portal:2:REQUEST\_DEPENDENCIES\]
- Portal 2 (ID 2) / requests: 1 affected records observed. The identified relationship requires a migration disposition. \[portal:2:REQUEST\_CHANGE\_LINKS\]
- Portal 3 (ID 3) / requests: 1 affected records observed. The identified relationship requires a migration disposition. \[portal:3:LINKED\_REQUESTS\]
- Portal 3 (ID 3) / requests: 1 affected records observed. The identified relationship requires a migration disposition. \[portal:3:REQUEST\_DEPENDENCIES\]
- Portal 3 (ID 3) / requests: 1 affected records observed. The identified relationship requires a migration disposition. \[portal:3:REQUEST\_CHANGE\_LINKS\]

#### API coverage limitations

- Environment / topology: Portal discovery did not certify all API-visible topology.
- Portal 1 (ID 1) / technicians: COMPLETE Records observed: 3. List complete: true.
- Portal 1 (ID 1) / reports: COMPLETE Records observed: 1. List complete: true.
- Portal 1 (ID 1) / cmdb: COMPLETE Records observed: 1. List complete: true.
- Portal 1 (ID 1) / assets: COMPLETE Records observed: 3. List complete: true.
- Portal 1 (ID 1) / requests: COMPLETE Records observed: 3. List complete: true.
- Portal 1 (ID 1) / assets: COMPLETE Records observed: 2. List complete: true.
- Portal 1 (ID 1) / cmdb: COMPLETE Records observed: 2. List complete: true.
- Portal 1 (ID 1) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- Portal 1 (ID 1) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- Portal 2 (ID 2) / technicians: COMPLETE Records observed: 3. List complete: true.
- Portal 2 (ID 2) / reports: COMPLETE Records observed: 1. List complete: true.
- Portal 2 (ID 2) / cmdb: COMPLETE Records observed: 1. List complete: true.
- Portal 2 (ID 2) / projects: PERMISSION\_DENIED Records observed: —. List complete: false.
- Portal 2 (ID 2) / assets: COMPLETE Records observed: 2. List complete: true.
- Portal 2 (ID 2) / cmdb: COMPLETE Records observed: 2. List complete: true.
- Portal 2 (ID 2) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- Portal 2 (ID 2) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- Portal 3 (ID 3) / technicians: COMPLETE Records observed: 3. List complete: true.
- Portal 3 (ID 3) / reports: COMPLETE Records observed: 1. List complete: true.
- Portal 3 (ID 3) / cmdb: COMPLETE Records observed: 1. List complete: true.
- Portal 3 (ID 3) / assets: COMPLETE Records observed: 3. List complete: true.
- Portal 3 (ID 3) / releases: MODULE\_NOT\_AVAILABLE Records observed: —. List complete: false.
- Portal 3 (ID 3) / assets: COMPLETE Records observed: 1. List complete: true.
- Portal 3 (ID 3) / cmdb: COMPLETE Records observed: 2. List complete: true.
- Portal 4 (ID 4) / requests: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / requests: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / sites: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / groups: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / technicians: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / users: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / reports: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / cmdb: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / assets: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / requests: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / changes: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / problems: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / projects: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / releases: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / assets: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / assets: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / cmdb: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / contracts: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / purchases: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Environment / orgusers: COMPLETE Records observed: 2. List complete: true.

#### Target-cloud unknowns

- Retained IDs, target URLs and email-threading behavior cannot be proven with source credentials.

#### Vendor confirmation required

- Confirm Change ID retention, per-portal ID cross-references, linked/dependent requests, request-change mappings and legacy links.

#### Project/business decision required

- Choose the cross-reference format and tests for each required relationship and historical link.

### Q5 · Which settings, fields, workflows, scripts, reports or modules require reconstruction or licensing?

#### Confirmed source evidence

- Portal 1 (ID 1) / technicians: 3 affected records observed. Resolve missing or shared technician email identities. \[portal:1:TECHNICIAN\_EMAILS\]
- Portal 1 (ID 1) / requests: 2 typed values checked; definitions, defaults, options, and uninspected record values may add exposure. \[portal:1:FIELD\_VALUE\_LENGTHS\]
- Portal 1 (ID 1) / multiple: 0 configuration objects and 4 record references observed. Source inventory does not verify target reconstruction. \[portal:1:WORKFLOW\_REBUILD\]
- Portal 1 (ID 1) / reports: 1 affected records observed. This query-report inventory may include built-ins; custom status and actual usage are not established. \[portal:1:QUERY\_REPORTS\]
- Portal 1 (ID 1) / templates: 2 templates exposed relevant nested metadata; 2 exceed a documented count limit. \[portal:1:TEMPLATE\_COMPLEXITY\]
- Portal 1 (ID 1) / requests: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:1:FIELD\_REQUESTS\_DEFAULT\_OPTION\_SIZE\]
- Portal 1 (ID 1) / requests: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:1:FIELD\_REQUESTS\_OPTION\_NORMALIZATION\]
- Portal 1 (ID 1) / changes: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:1:FIELD\_CHANGES\_DEFAULT\_OPTION\_SIZE\]
- Portal 1 (ID 1) / changes: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:1:FIELD\_CHANGES\_OPTION\_NORMALIZATION\]
- Portal 1 (ID 1) / assets: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:1:FIELD\_ASSETS\_DEFAULT\_OPTION\_SIZE\]
- Portal 1 (ID 1) / assets: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:1:FIELD\_ASSETS\_OPTION\_NORMALIZATION\]
- Portal 1 (ID 1) / computers: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:1:FIELD\_COMPUTERS\_DEFAULT\_OPTION\_SIZE\]
- Portal 1 (ID 1) / computers: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:1:FIELD\_COMPUTERS\_OPTION\_NORMALIZATION\]
- Portal 1 (ID 1) / cis: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:1:FIELD\_CIS\_DEFAULT\_OPTION\_SIZE\]
- Portal 1 (ID 1) / cis: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:1:FIELD\_CIS\_OPTION\_NORMALIZATION\]
- Portal 2 (ID 2) / technicians: 3 affected records observed. Resolve missing or shared technician email identities. \[portal:2:TECHNICIAN\_EMAILS\]
- Portal 2 (ID 2) / requests: 2 typed values checked; definitions, defaults, options, and uninspected record values may add exposure. \[portal:2:FIELD\_VALUE\_LENGTHS\]
- Portal 2 (ID 2) / multiple: 0 configuration objects and 4 record references observed. Source inventory does not verify target reconstruction. \[portal:2:WORKFLOW\_REBUILD\]
- Portal 2 (ID 2) / reports: 1 affected records observed. This query-report inventory may include built-ins; custom status and actual usage are not established. \[portal:2:QUERY\_REPORTS\]
- Portal 2 (ID 2) / templates: 2 templates exposed relevant nested metadata; 2 exceed a documented count limit. \[portal:2:TEMPLATE\_COMPLEXITY\]
- Portal 2 (ID 2) / requests: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:2:FIELD\_REQUESTS\_DEFAULT\_OPTION\_SIZE\]
- Portal 2 (ID 2) / requests: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:2:FIELD\_REQUESTS\_OPTION\_NORMALIZATION\]
- Portal 2 (ID 2) / changes: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:2:FIELD\_CHANGES\_DEFAULT\_OPTION\_SIZE\]
- Portal 2 (ID 2) / changes: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:2:FIELD\_CHANGES\_OPTION\_NORMALIZATION\]
- Portal 2 (ID 2) / assets: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:2:FIELD\_ASSETS\_DEFAULT\_OPTION\_SIZE\]
- Portal 2 (ID 2) / assets: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:2:FIELD\_ASSETS\_OPTION\_NORMALIZATION\]
- Portal 2 (ID 2) / computers: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:2:FIELD\_COMPUTERS\_DEFAULT\_OPTION\_SIZE\]
- Portal 2 (ID 2) / computers: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:2:FIELD\_COMPUTERS\_OPTION\_NORMALIZATION\]
- Portal 3 (ID 3) / technicians: 3 affected records observed. Resolve missing or shared technician email identities. \[portal:3:TECHNICIAN\_EMAILS\]
- Portal 3 (ID 3) / requests: 1 typed values checked; definitions, defaults, options, and uninspected record values may add exposure. \[portal:3:FIELD\_VALUE\_LENGTHS\]
- Portal 3 (ID 3) / multiple: 0 configuration objects and 3 record references observed. Source inventory does not verify target reconstruction. \[portal:3:WORKFLOW\_REBUILD\]
- Portal 3 (ID 3) / reports: 1 affected records observed. This query-report inventory may include built-ins; custom status and actual usage are not established. \[portal:3:QUERY\_REPORTS\]
- Portal 3 (ID 3) / templates: 2 templates exposed relevant nested metadata; 2 exceed a documented count limit. \[portal:3:TEMPLATE\_COMPLEXITY\]
- Portal 3 (ID 3) / changes: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:3:FIELD\_CHANGES\_DEFAULT\_OPTION\_SIZE\]
- Portal 3 (ID 3) / changes: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:3:FIELD\_CHANGES\_OPTION\_NORMALIZATION\]
- Portal 3 (ID 3) / assets: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:3:FIELD\_ASSETS\_DEFAULT\_OPTION\_SIZE\]
- Portal 3 (ID 3) / assets: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:3:FIELD\_ASSETS\_OPTION\_NORMALIZATION\]
- Portal 3 (ID 3) / computers: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:3:FIELD\_COMPUTERS\_DEFAULT\_OPTION\_SIZE\]
- Portal 3 (ID 3) / computers: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:3:FIELD\_COMPUTERS\_OPTION\_NORMALIZATION\]

#### API coverage limitations

- Environment / topology: Portal discovery did not certify all API-visible topology.
- Portal 1 (ID 1) / technicians: COMPLETE Records observed: 3. List complete: true.
- Portal 1 (ID 1) / reports: COMPLETE Records observed: 1. List complete: true.
- Portal 1 (ID 1) / cmdb: COMPLETE Records observed: 1. List complete: true.
- Portal 1 (ID 1) / assets: COMPLETE Records observed: 3. List complete: true.
- Portal 1 (ID 1) / requests: COMPLETE Records observed: 3. List complete: true.
- Portal 1 (ID 1) / assets: COMPLETE Records observed: 2. List complete: true.
- Portal 1 (ID 1) / cmdb: COMPLETE Records observed: 2. List complete: true.
- Portal 1 (ID 1) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- Portal 1 (ID 1) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- Portal 2 (ID 2) / technicians: COMPLETE Records observed: 3. List complete: true.
- Portal 2 (ID 2) / reports: COMPLETE Records observed: 1. List complete: true.
- Portal 2 (ID 2) / cmdb: COMPLETE Records observed: 1. List complete: true.
- Portal 2 (ID 2) / projects: PERMISSION\_DENIED Records observed: —. List complete: false.
- Portal 2 (ID 2) / assets: COMPLETE Records observed: 2. List complete: true.
- Portal 2 (ID 2) / cmdb: COMPLETE Records observed: 2. List complete: true.
- Portal 2 (ID 2) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- Portal 2 (ID 2) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- Portal 3 (ID 3) / technicians: COMPLETE Records observed: 3. List complete: true.
- Portal 3 (ID 3) / reports: COMPLETE Records observed: 1. List complete: true.
- Portal 3 (ID 3) / cmdb: COMPLETE Records observed: 1. List complete: true.
- Portal 3 (ID 3) / assets: COMPLETE Records observed: 3. List complete: true.
- Portal 3 (ID 3) / releases: MODULE\_NOT\_AVAILABLE Records observed: —. List complete: false.
- Portal 3 (ID 3) / assets: COMPLETE Records observed: 1. List complete: true.
- Portal 3 (ID 3) / cmdb: COMPLETE Records observed: 2. List complete: true.
- Portal 4 (ID 4) / requests: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / requests: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / sites: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / groups: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / technicians: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / users: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / reports: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / cmdb: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / assets: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / requests: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / changes: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / problems: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / projects: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / releases: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / assets: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / assets: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / cmdb: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / contracts: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / purchases: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Environment / orgusers: COMPLETE Records observed: 2. List complete: true.
- Portal 1 (ID 1) / requests: 3 distinct additional fields observed; 3 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_REQUESTS\_COVERAGE\]
- Portal 1 (ID 1) / requests: 3 distinct additional fields observed; the documented total limit is 250. Target edition and per-type mapping still require confirmation. \[portal:1:FIELD\_REQUESTS\_CAPACITY\]
- Portal 1 (ID 1) / problems: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_PROBLEMS\_COVERAGE\]
- Portal 1 (ID 1) / problems: 1 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:1:FIELD\_PROBLEMS\_CAPACITY\]
- Portal 1 (ID 1) / changes: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_CHANGES\_COVERAGE\]
- Portal 1 (ID 1) / changes: 2 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:1:FIELD\_CHANGES\_CAPACITY\]
- Portal 1 (ID 1) / projects: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_PROJECTS\_COVERAGE\]
- Portal 1 (ID 1) / projects: 1 distinct additional fields observed; the documented total limit is 110. Target edition and per-type mapping still require confirmation. \[portal:1:FIELD\_PROJECTS\_CAPACITY\]
- Portal 1 (ID 1) / releases: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_RELEASES\_COVERAGE\]
- Portal 1 (ID 1) / releases: 1 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:1:FIELD\_RELEASES\_CAPACITY\]
- Portal 1 (ID 1) / users: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_USERS\_COVERAGE\]
- Portal 1 (ID 1) / users: 1 distinct additional fields observed; the documented total limit is 50. Target edition and per-type mapping still require confirmation. \[portal:1:FIELD\_USERS\_CAPACITY\]
- Portal 1 (ID 1) / technicians: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_TECHNICIANS\_COVERAGE\]
- Portal 1 (ID 1) / technicians: Additional-field count is unknown; the documented total limit is 50. Target edition and per-type mapping still require confirmation. \[portal:1:FIELD\_TECHNICIANS\_CAPACITY\]
- Portal 1 (ID 1) / assets: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_ASSETS\_COVERAGE\]
- Portal 1 (ID 1) / assets: 2 distinct additional fields observed; the documented total limit is 100. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. \[portal:1:FIELD\_ASSETS\_CAPACITY\]
- Portal 1 (ID 1) / computers: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_COMPUTERS\_COVERAGE\]
- Portal 1 (ID 1) / computers: 2 distinct additional fields observed; the documented total limit is 52. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. \[portal:1:FIELD\_COMPUTERS\_CAPACITY\]
- Portal 1 (ID 1) / cis: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_CIS\_COVERAGE\]
- Portal 1 (ID 1) / cis: 2 distinct additional fields observed; the documented total limit is 1560. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. \[portal:1:FIELD\_CIS\_CAPACITY\]
- Portal 1 (ID 1) / contracts: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_CONTRACTS\_COVERAGE\]
- Portal 1 (ID 1) / contracts: Additional-field count is unknown; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:1:FIELD\_CONTRACTS\_CAPACITY\]
- Portal 1 (ID 1) / purchases: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_PURCHASES\_COVERAGE\]
- Portal 1 (ID 1) / purchases: Additional-field count is unknown; the documented total limit is 164. Target edition and per-type mapping still require confirmation. \[portal:1:FIELD\_PURCHASES\_CAPACITY\]
- Portal 2 (ID 2) / requests: 3 distinct additional fields observed; 3 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_REQUESTS\_COVERAGE\]
- Portal 2 (ID 2) / requests: 3 distinct additional fields observed; the documented total limit is 250. Target edition and per-type mapping still require confirmation. \[portal:2:FIELD\_REQUESTS\_CAPACITY\]
- Portal 2 (ID 2) / problems: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_PROBLEMS\_COVERAGE\]
- Portal 2 (ID 2) / problems: 1 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:2:FIELD\_PROBLEMS\_CAPACITY\]
- Portal 2 (ID 2) / changes: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_CHANGES\_COVERAGE\]
- Portal 2 (ID 2) / changes: 2 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:2:FIELD\_CHANGES\_CAPACITY\]
- Portal 2 (ID 2) / projects: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_PROJECTS\_COVERAGE\]
- Portal 2 (ID 2) / projects: Additional-field count is unknown; the documented total limit is 110. Target edition and per-type mapping still require confirmation. \[portal:2:FIELD\_PROJECTS\_CAPACITY\]
- Portal 2 (ID 2) / releases: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_RELEASES\_COVERAGE\]
- Portal 2 (ID 2) / releases: 1 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:2:FIELD\_RELEASES\_CAPACITY\]
- Portal 2 (ID 2) / users: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_USERS\_COVERAGE\]
- Portal 2 (ID 2) / users: 1 distinct additional fields observed; the documented total limit is 50. Target edition and per-type mapping still require confirmation. \[portal:2:FIELD\_USERS\_CAPACITY\]
- Portal 2 (ID 2) / technicians: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_TECHNICIANS\_COVERAGE\]
- Portal 2 (ID 2) / technicians: Additional-field count is unknown; the documented total limit is 50. Target edition and per-type mapping still require confirmation. \[portal:2:FIELD\_TECHNICIANS\_CAPACITY\]
- Portal 2 (ID 2) / assets: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: PARTIAL. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_ASSETS\_COVERAGE\]
- Portal 2 (ID 2) / assets: 2 distinct additional fields observed; the documented total limit is 100. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. \[portal:2:FIELD\_ASSETS\_CAPACITY\]
- Portal 2 (ID 2) / computers: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_COMPUTERS\_COVERAGE\]
- Portal 2 (ID 2) / computers: 2 distinct additional fields observed; the documented total limit is 52. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. \[portal:2:FIELD\_COMPUTERS\_CAPACITY\]
- Portal 2 (ID 2) / cis: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_CIS\_COVERAGE\]
- Portal 2 (ID 2) / cis: 1 distinct additional fields observed; the documented total limit is 1560. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. \[portal:2:FIELD\_CIS\_CAPACITY\]
- Portal 2 (ID 2) / contracts: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_CONTRACTS\_COVERAGE\]
- Portal 2 (ID 2) / contracts: Additional-field count is unknown; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:2:FIELD\_CONTRACTS\_CAPACITY\]
- Portal 2 (ID 2) / purchases: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_PURCHASES\_COVERAGE\]
- Portal 2 (ID 2) / purchases: Additional-field count is unknown; the documented total limit is 164. Target edition and per-type mapping still require confirmation. \[portal:2:FIELD\_PURCHASES\_CAPACITY\]
- Portal 3 (ID 3) / requests: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_REQUESTS\_COVERAGE\]
- Portal 3 (ID 3) / requests: 1 distinct additional fields observed; the documented total limit is 250. Target edition and per-type mapping still require confirmation. \[portal:3:FIELD\_REQUESTS\_CAPACITY\]
- Portal 3 (ID 3) / problems: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_PROBLEMS\_COVERAGE\]
- Portal 3 (ID 3) / problems: 1 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:3:FIELD\_PROBLEMS\_CAPACITY\]
- Portal 3 (ID 3) / changes: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_CHANGES\_COVERAGE\]
- Portal 3 (ID 3) / changes: 2 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:3:FIELD\_CHANGES\_CAPACITY\]
- Portal 3 (ID 3) / projects: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_PROJECTS\_COVERAGE\]
- Portal 3 (ID 3) / projects: 1 distinct additional fields observed; the documented total limit is 110. Target edition and per-type mapping still require confirmation. \[portal:3:FIELD\_PROJECTS\_CAPACITY\]
- Portal 3 (ID 3) / releases: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_RELEASES\_COVERAGE\]
- Portal 3 (ID 3) / releases: Additional-field count is unknown; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:3:FIELD\_RELEASES\_CAPACITY\]
- Portal 3 (ID 3) / users: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_USERS\_COVERAGE\]
- Portal 3 (ID 3) / users: 1 distinct additional fields observed; the documented total limit is 50. Target edition and per-type mapping still require confirmation. \[portal:3:FIELD\_USERS\_CAPACITY\]
- Portal 3 (ID 3) / technicians: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_TECHNICIANS\_COVERAGE\]
- Portal 3 (ID 3) / technicians: Additional-field count is unknown; the documented total limit is 50. Target edition and per-type mapping still require confirmation. \[portal:3:FIELD\_TECHNICIANS\_CAPACITY\]
- Portal 3 (ID 3) / assets: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_ASSETS\_COVERAGE\]
- Portal 3 (ID 3) / assets: 2 distinct additional fields observed; the documented total limit is 100. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. \[portal:3:FIELD\_ASSETS\_CAPACITY\]
- Portal 3 (ID 3) / computers: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_COMPUTERS\_COVERAGE\]
- Portal 3 (ID 3) / computers: 2 distinct additional fields observed; the documented total limit is 52. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. \[portal:3:FIELD\_COMPUTERS\_CAPACITY\]
- Portal 3 (ID 3) / cis: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_CIS\_COVERAGE\]
- Portal 3 (ID 3) / cis: 1 distinct additional fields observed; the documented total limit is 1560. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. \[portal:3:FIELD\_CIS\_CAPACITY\]
- Portal 3 (ID 3) / contracts: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_CONTRACTS\_COVERAGE\]
- Portal 3 (ID 3) / contracts: Additional-field count is unknown; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:3:FIELD\_CONTRACTS\_CAPACITY\]
- Portal 3 (ID 3) / purchases: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_PURCHASES\_COVERAGE\]
- Portal 3 (ID 3) / purchases: Additional-field count is unknown; the documented total limit is 164. Target edition and per-type mapping still require confirmation. \[portal:3:FIELD\_PURCHASES\_CAPACITY\]
- Portal 4 (ID 4) / requests: 0 distinct request-field definitions observed; 0 have recognized types. The combined paid-tier limit is 250. \[portal:4:REQUEST\_FIELD\_CAPACITY\]
- Portal 4 (ID 4) / requests: No matching issue established from 0 checked records; collection or required-field coverage is incomplete. \[portal:4:FIELD\_NAME\_COLLISIONS\]
- Portal 4 (ID 4) / requests: 0 typed values checked; definitions, defaults, options, and uninspected record values may add exposure. \[portal:4:FIELD\_VALUE\_LENGTHS\]

#### Target-cloud unknowns

- Target entitlements, runtime support, quotas and functional equivalents remain unverified.

#### Vendor confirmation required

- Confirm field/type mapping, SLA and lifecycle/workflow matching, unsupported form actions, reporting paths, module licenses and discovery architecture.

#### Project/business decision required

- Assign owners to reconstruction and external integrations; agree which behaviors must be equivalent at go-live.

### Q6 · What export and recovery capabilities require confirmation?

#### Confirmed source evidence

No applicable evidence established; absence or target compatibility is not certified.

#### API coverage limitations

- Environment / topology: Portal discovery did not certify all API-visible topology.
- Portal 1 (ID 1) / technicians: COMPLETE Records observed: 3. List complete: true.
- Portal 1 (ID 1) / reports: COMPLETE Records observed: 1. List complete: true.
- Portal 1 (ID 1) / cmdb: COMPLETE Records observed: 1. List complete: true.
- Portal 1 (ID 1) / assets: COMPLETE Records observed: 3. List complete: true.
- Portal 1 (ID 1) / requests: COMPLETE Records observed: 3. List complete: true.
- Portal 1 (ID 1) / assets: COMPLETE Records observed: 2. List complete: true.
- Portal 1 (ID 1) / cmdb: COMPLETE Records observed: 2. List complete: true.
- Portal 1 (ID 1) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- Portal 1 (ID 1) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- Portal 2 (ID 2) / technicians: COMPLETE Records observed: 3. List complete: true.
- Portal 2 (ID 2) / reports: COMPLETE Records observed: 1. List complete: true.
- Portal 2 (ID 2) / cmdb: COMPLETE Records observed: 1. List complete: true.
- Portal 2 (ID 2) / projects: PERMISSION\_DENIED Records observed: —. List complete: false.
- Portal 2 (ID 2) / assets: COMPLETE Records observed: 2. List complete: true.
- Portal 2 (ID 2) / cmdb: COMPLETE Records observed: 2. List complete: true.
- Portal 2 (ID 2) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- Portal 2 (ID 2) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- Portal 3 (ID 3) / technicians: COMPLETE Records observed: 3. List complete: true.
- Portal 3 (ID 3) / reports: COMPLETE Records observed: 1. List complete: true.
- Portal 3 (ID 3) / cmdb: COMPLETE Records observed: 1. List complete: true.
- Portal 3 (ID 3) / assets: COMPLETE Records observed: 3. List complete: true.
- Portal 3 (ID 3) / releases: MODULE\_NOT\_AVAILABLE Records observed: —. List complete: false.
- Portal 3 (ID 3) / assets: COMPLETE Records observed: 1. List complete: true.
- Portal 3 (ID 3) / cmdb: COMPLETE Records observed: 2. List complete: true.
- Portal 4 (ID 4) / requests: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / requests: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / sites: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / groups: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / technicians: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / users: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / reports: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / cmdb: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / assets: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / requests: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / changes: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / problems: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / projects: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / releases: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / assets: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / assets: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / cmdb: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / contracts: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / purchases: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Environment / orgusers: COMPLETE Records observed: 2. List complete: true.

#### Target-cloud unknowns

- The scan does not inspect Cloud backup/export configuration or prove restore and exit capabilities.

#### Vendor confirmation required

- Obtain tenant-specific export completeness/frequency, recovery granularity, RPO/RTO, support involvement and exit commitments.

#### Project/business decision required

- Define retention, recovery objectives, periodic export ownership and when source retirement is permitted.

### Q7 · Which failures or unresolved differences should block migration acceptance?

#### Confirmed source evidence

- Portal 1 (ID 1) / multiple: 5 affected records observed. An agreed historical-data disposition is required. \[portal:1:HISTORY\_WINDOW\_ONE\_YEAR\]
- Portal 1 (ID 1) / multiple: 1 affected records observed. An agreed historical-data disposition is required. \[portal:1:HISTORY\_WINDOW\_FIVE\_YEARS\]
- Portal 1 (ID 1) / requests: 1 affected records observed. The identified relationship requires a migration disposition. \[portal:1:LINKED\_REQUESTS\]
- Portal 1 (ID 1) / requests: 1 affected records observed. The identified relationship requires a migration disposition. \[portal:1:REQUEST\_DEPENDENCIES\]
- Portal 1 (ID 1) / requests: 1 affected records observed. The identified relationship requires a migration disposition. \[portal:1:REQUEST\_CHANGE\_LINKS\]
- Portal 1 (ID 1) / multiple: 1 observed owner totals exceed both interpretations of 48 MB. \[portal:1:ATTACHMENT\_SIZE\]
- Portal 1 (ID 1) / requests: 1 affected records observed. Identified note attachments require separate preservation. \[portal:1:NOTE\_ATTACHMENTS\]
- Portal 1 (ID 1) / technicians: 3 affected records observed. Resolve missing or shared technician email identities. \[portal:1:TECHNICIAN\_EMAILS\]
- Portal 1 (ID 1) / requests: 2 typed values checked; definitions, defaults, options, and uninspected record values may add exposure. \[portal:1:FIELD\_VALUE\_LENGTHS\]
- Portal 1 (ID 1) / requests: 1 affected records observed. The observed date ordering needs remediation. \[portal:1:REQUEST\_SCHEDULE\_DATES\]
- Portal 1 (ID 1) / computers: 2 affected records observed. Duplicate tags require a supported migration treatment. \[portal:1:DUPLICATE\_SERVICE\_TAGS\]
- Portal 1 (ID 1) / assets: 1 affected records observed. Observed date ordering can change migrated values. \[portal:1:ASSET\_DATE\_ORDER\]
- Portal 1 (ID 1) / multiple: 0 configuration objects and 4 record references observed. Source inventory does not verify target reconstruction. \[portal:1:WORKFLOW\_REBUILD\]
- Portal 1 (ID 1) / reports: 1 affected records observed. This query-report inventory may include built-ins; custom status and actual usage are not established. \[portal:1:QUERY\_REPORTS\]
- Portal 1 (ID 1) / templates: 2 templates exposed relevant nested metadata; 2 exceed a documented count limit. \[portal:1:TEMPLATE\_COMPLEXITY\]
- Portal 1 (ID 1) / requests: 1 resolution values measured; 1 exceed the documented limit. \[portal:1:RESOLUTION\_LENGTH\]
- Portal 1 (ID 1) / problems: 1 problems have observed ancillary content; unexposed problem configuration remains unassessed. \[portal:1:PROBLEM\_ANCILLARY\_DATA\]
- Portal 1 (ID 1) / requests: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:1:FIELD\_REQUESTS\_DEFAULT\_OPTION\_SIZE\]
- Portal 1 (ID 1) / requests: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:1:FIELD\_REQUESTS\_OPTION\_NORMALIZATION\]
- Portal 1 (ID 1) / changes: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:1:FIELD\_CHANGES\_DEFAULT\_OPTION\_SIZE\]
- Portal 1 (ID 1) / changes: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:1:FIELD\_CHANGES\_OPTION\_NORMALIZATION\]
- Portal 1 (ID 1) / assets: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:1:FIELD\_ASSETS\_DEFAULT\_OPTION\_SIZE\]
- Portal 1 (ID 1) / assets: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:1:FIELD\_ASSETS\_OPTION\_NORMALIZATION\]
- Portal 1 (ID 1) / computers: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:1:FIELD\_COMPUTERS\_DEFAULT\_OPTION\_SIZE\]
- Portal 1 (ID 1) / computers: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:1:FIELD\_COMPUTERS\_OPTION\_NORMALIZATION\]
- Portal 1 (ID 1) / cis: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:1:FIELD\_CIS\_DEFAULT\_OPTION\_SIZE\]
- Portal 1 (ID 1) / cis: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:1:FIELD\_CIS\_OPTION\_NORMALIZATION\]
- Portal 2 (ID 2) / multiple: 4 affected records observed. An agreed historical-data disposition is required. \[portal:2:HISTORY\_WINDOW\_ONE\_YEAR\]
- Portal 2 (ID 2) / multiple: 1 affected records observed. An agreed historical-data disposition is required. \[portal:2:HISTORY\_WINDOW\_FIVE\_YEARS\]
- Portal 2 (ID 2) / requests: 1 affected records observed. The identified relationship requires a migration disposition. \[portal:2:LINKED\_REQUESTS\]
- Portal 2 (ID 2) / requests: 1 affected records observed. The identified relationship requires a migration disposition. \[portal:2:REQUEST\_DEPENDENCIES\]
- Portal 2 (ID 2) / requests: 1 affected records observed. The identified relationship requires a migration disposition. \[portal:2:REQUEST\_CHANGE\_LINKS\]
- Portal 2 (ID 2) / multiple: 1 observed owner totals exceed both interpretations of 48 MB. \[portal:2:ATTACHMENT\_SIZE\]
- Portal 2 (ID 2) / requests: 1 affected records observed. Identified note attachments require separate preservation. \[portal:2:NOTE\_ATTACHMENTS\]
- Portal 2 (ID 2) / technicians: 3 affected records observed. Resolve missing or shared technician email identities. \[portal:2:TECHNICIAN\_EMAILS\]
- Portal 2 (ID 2) / requests: 2 typed values checked; definitions, defaults, options, and uninspected record values may add exposure. \[portal:2:FIELD\_VALUE\_LENGTHS\]
- Portal 2 (ID 2) / requests: 1 affected records observed. The observed date ordering needs remediation. \[portal:2:REQUEST\_SCHEDULE\_DATES\]
- Portal 2 (ID 2) / computers: 2 affected records observed. Duplicate tags require a supported migration treatment. \[portal:2:DUPLICATE\_SERVICE\_TAGS\]
- Portal 2 (ID 2) / assets: 1 affected records observed. Observed date ordering can change migrated values. \[portal:2:ASSET\_DATE\_ORDER\]
- Portal 2 (ID 2) / multiple: 0 configuration objects and 4 record references observed. Source inventory does not verify target reconstruction. \[portal:2:WORKFLOW\_REBUILD\]
- Portal 2 (ID 2) / reports: 1 affected records observed. This query-report inventory may include built-ins; custom status and actual usage are not established. \[portal:2:QUERY\_REPORTS\]
- Portal 2 (ID 2) / templates: 2 templates exposed relevant nested metadata; 2 exceed a documented count limit. \[portal:2:TEMPLATE\_COMPLEXITY\]
- Portal 2 (ID 2) / requests: 1 resolution values measured; 1 exceed the documented limit. \[portal:2:RESOLUTION\_LENGTH\]
- Portal 2 (ID 2) / problems: 1 problems have observed ancillary content; unexposed problem configuration remains unassessed. \[portal:2:PROBLEM\_ANCILLARY\_DATA\]
- Portal 2 (ID 2) / requests: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:2:FIELD\_REQUESTS\_DEFAULT\_OPTION\_SIZE\]
- Portal 2 (ID 2) / requests: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:2:FIELD\_REQUESTS\_OPTION\_NORMALIZATION\]
- Portal 2 (ID 2) / changes: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:2:FIELD\_CHANGES\_DEFAULT\_OPTION\_SIZE\]
- Portal 2 (ID 2) / changes: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:2:FIELD\_CHANGES\_OPTION\_NORMALIZATION\]
- Portal 2 (ID 2) / assets: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:2:FIELD\_ASSETS\_DEFAULT\_OPTION\_SIZE\]
- Portal 2 (ID 2) / assets: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:2:FIELD\_ASSETS\_OPTION\_NORMALIZATION\]
- Portal 2 (ID 2) / computers: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:2:FIELD\_COMPUTERS\_DEFAULT\_OPTION\_SIZE\]
- Portal 2 (ID 2) / computers: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:2:FIELD\_COMPUTERS\_OPTION\_NORMALIZATION\]
- Portal 3 (ID 3) / multiple: 4 affected records observed. An agreed historical-data disposition is required. \[portal:3:HISTORY\_WINDOW\_ONE\_YEAR\]
- Portal 3 (ID 3) / multiple: 1 affected records observed. An agreed historical-data disposition is required. \[portal:3:HISTORY\_WINDOW\_FIVE\_YEARS\]
- Portal 3 (ID 3) / requests: 1 affected records observed. The identified relationship requires a migration disposition. \[portal:3:LINKED\_REQUESTS\]
- Portal 3 (ID 3) / requests: 1 affected records observed. The identified relationship requires a migration disposition. \[portal:3:REQUEST\_DEPENDENCIES\]
- Portal 3 (ID 3) / requests: 1 affected records observed. The identified relationship requires a migration disposition. \[portal:3:REQUEST\_CHANGE\_LINKS\]
- Portal 3 (ID 3) / multiple: 1 observed owner totals exceed both interpretations of 48 MB. \[portal:3:ATTACHMENT\_SIZE\]
- Portal 3 (ID 3) / requests: 1 affected records observed. Identified note attachments require separate preservation. \[portal:3:NOTE\_ATTACHMENTS\]
- Portal 3 (ID 3) / technicians: 3 affected records observed. Resolve missing or shared technician email identities. \[portal:3:TECHNICIAN\_EMAILS\]
- Portal 3 (ID 3) / requests: 1 typed values checked; definitions, defaults, options, and uninspected record values may add exposure. \[portal:3:FIELD\_VALUE\_LENGTHS\]
- Portal 3 (ID 3) / requests: 1 affected records observed. The observed date ordering needs remediation. \[portal:3:REQUEST\_SCHEDULE\_DATES\]
- Portal 3 (ID 3) / assets: 1 affected records observed. Observed date ordering can change migrated values. \[portal:3:ASSET\_DATE\_ORDER\]
- Portal 3 (ID 3) / multiple: 0 configuration objects and 3 record references observed. Source inventory does not verify target reconstruction. \[portal:3:WORKFLOW\_REBUILD\]
- Portal 3 (ID 3) / reports: 1 affected records observed. This query-report inventory may include built-ins; custom status and actual usage are not established. \[portal:3:QUERY\_REPORTS\]
- Portal 3 (ID 3) / templates: 2 templates exposed relevant nested metadata; 2 exceed a documented count limit. \[portal:3:TEMPLATE\_COMPLEXITY\]
- Portal 3 (ID 3) / requests: 1 resolution values measured; 1 exceed the documented limit. \[portal:3:RESOLUTION\_LENGTH\]
- Portal 3 (ID 3) / problems: 1 problems have observed ancillary content; unexposed problem configuration remains unassessed. \[portal:3:PROBLEM\_ANCILLARY\_DATA\]
- Portal 3 (ID 3) / changes: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:3:FIELD\_CHANGES\_DEFAULT\_OPTION\_SIZE\]
- Portal 3 (ID 3) / changes: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:3:FIELD\_CHANGES\_OPTION\_NORMALIZATION\]
- Portal 3 (ID 3) / assets: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:3:FIELD\_ASSETS\_DEFAULT\_OPTION\_SIZE\]
- Portal 3 (ID 3) / assets: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:3:FIELD\_ASSETS\_OPTION\_NORMALIZATION\]
- Portal 3 (ID 3) / computers: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:3:FIELD\_COMPUTERS\_DEFAULT\_OPTION\_SIZE\]
- Portal 3 (ID 3) / computers: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:3:FIELD\_COMPUTERS\_OPTION\_NORMALIZATION\]

#### API coverage limitations

- Environment / topology: Portal discovery did not certify all API-visible topology.
- Portal 1 (ID 1) / technicians: COMPLETE Records observed: 3. List complete: true.
- Portal 1 (ID 1) / reports: COMPLETE Records observed: 1. List complete: true.
- Portal 1 (ID 1) / cmdb: COMPLETE Records observed: 1. List complete: true.
- Portal 1 (ID 1) / assets: COMPLETE Records observed: 3. List complete: true.
- Portal 1 (ID 1) / requests: COMPLETE Records observed: 3. List complete: true.
- Portal 1 (ID 1) / assets: COMPLETE Records observed: 2. List complete: true.
- Portal 1 (ID 1) / cmdb: COMPLETE Records observed: 2. List complete: true.
- Portal 1 (ID 1) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- Portal 1 (ID 1) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- Portal 2 (ID 2) / technicians: COMPLETE Records observed: 3. List complete: true.
- Portal 2 (ID 2) / reports: COMPLETE Records observed: 1. List complete: true.
- Portal 2 (ID 2) / cmdb: COMPLETE Records observed: 1. List complete: true.
- Portal 2 (ID 2) / projects: PERMISSION\_DENIED Records observed: —. List complete: false.
- Portal 2 (ID 2) / assets: COMPLETE Records observed: 2. List complete: true.
- Portal 2 (ID 2) / cmdb: COMPLETE Records observed: 2. List complete: true.
- Portal 2 (ID 2) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- Portal 2 (ID 2) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- Portal 3 (ID 3) / technicians: COMPLETE Records observed: 3. List complete: true.
- Portal 3 (ID 3) / reports: COMPLETE Records observed: 1. List complete: true.
- Portal 3 (ID 3) / cmdb: COMPLETE Records observed: 1. List complete: true.
- Portal 3 (ID 3) / assets: COMPLETE Records observed: 3. List complete: true.
- Portal 3 (ID 3) / releases: MODULE\_NOT\_AVAILABLE Records observed: —. List complete: false.
- Portal 3 (ID 3) / assets: COMPLETE Records observed: 1. List complete: true.
- Portal 3 (ID 3) / cmdb: COMPLETE Records observed: 2. List complete: true.
- Portal 4 (ID 4) / requests: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / requests: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / sites: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / groups: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / technicians: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / users: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / reports: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / cmdb: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / assets: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / requests: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / changes: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / problems: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / projects: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / releases: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / assets: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / assets: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / cmdb: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / contracts: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Portal 4 (ID 4) / purchases: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Environment / orgusers: COMPLETE Records observed: 2. List complete: true.
- Portal 1 (ID 1) / requests: 3 distinct additional fields observed; 3 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_REQUESTS\_COVERAGE\]
- Portal 1 (ID 1) / requests: 3 distinct additional fields observed; the documented total limit is 250. Target edition and per-type mapping still require confirmation. \[portal:1:FIELD\_REQUESTS\_CAPACITY\]
- Portal 1 (ID 1) / problems: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_PROBLEMS\_COVERAGE\]
- Portal 1 (ID 1) / problems: 1 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:1:FIELD\_PROBLEMS\_CAPACITY\]
- Portal 1 (ID 1) / changes: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_CHANGES\_COVERAGE\]
- Portal 1 (ID 1) / changes: 2 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:1:FIELD\_CHANGES\_CAPACITY\]
- Portal 1 (ID 1) / projects: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_PROJECTS\_COVERAGE\]
- Portal 1 (ID 1) / projects: 1 distinct additional fields observed; the documented total limit is 110. Target edition and per-type mapping still require confirmation. \[portal:1:FIELD\_PROJECTS\_CAPACITY\]
- Portal 1 (ID 1) / releases: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_RELEASES\_COVERAGE\]
- Portal 1 (ID 1) / releases: 1 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:1:FIELD\_RELEASES\_CAPACITY\]
- Portal 1 (ID 1) / users: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_USERS\_COVERAGE\]
- Portal 1 (ID 1) / users: 1 distinct additional fields observed; the documented total limit is 50. Target edition and per-type mapping still require confirmation. \[portal:1:FIELD\_USERS\_CAPACITY\]
- Portal 1 (ID 1) / technicians: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_TECHNICIANS\_COVERAGE\]
- Portal 1 (ID 1) / technicians: Additional-field count is unknown; the documented total limit is 50. Target edition and per-type mapping still require confirmation. \[portal:1:FIELD\_TECHNICIANS\_CAPACITY\]
- Portal 1 (ID 1) / assets: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_ASSETS\_COVERAGE\]
- Portal 1 (ID 1) / assets: 2 distinct additional fields observed; the documented total limit is 100. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. \[portal:1:FIELD\_ASSETS\_CAPACITY\]
- Portal 1 (ID 1) / computers: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_COMPUTERS\_COVERAGE\]
- Portal 1 (ID 1) / computers: 2 distinct additional fields observed; the documented total limit is 52. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. \[portal:1:FIELD\_COMPUTERS\_CAPACITY\]
- Portal 1 (ID 1) / cis: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_CIS\_COVERAGE\]
- Portal 1 (ID 1) / cis: 2 distinct additional fields observed; the documented total limit is 1560. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. \[portal:1:FIELD\_CIS\_CAPACITY\]
- Portal 1 (ID 1) / contracts: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_CONTRACTS\_COVERAGE\]
- Portal 1 (ID 1) / contracts: Additional-field count is unknown; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:1:FIELD\_CONTRACTS\_CAPACITY\]
- Portal 1 (ID 1) / purchases: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_PURCHASES\_COVERAGE\]
- Portal 1 (ID 1) / purchases: Additional-field count is unknown; the documented total limit is 164. Target edition and per-type mapping still require confirmation. \[portal:1:FIELD\_PURCHASES\_CAPACITY\]
- Portal 2 (ID 2) / requests: 3 distinct additional fields observed; 3 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_REQUESTS\_COVERAGE\]
- Portal 2 (ID 2) / requests: 3 distinct additional fields observed; the documented total limit is 250. Target edition and per-type mapping still require confirmation. \[portal:2:FIELD\_REQUESTS\_CAPACITY\]
- Portal 2 (ID 2) / problems: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_PROBLEMS\_COVERAGE\]
- Portal 2 (ID 2) / problems: 1 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:2:FIELD\_PROBLEMS\_CAPACITY\]
- Portal 2 (ID 2) / changes: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_CHANGES\_COVERAGE\]
- Portal 2 (ID 2) / changes: 2 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:2:FIELD\_CHANGES\_CAPACITY\]
- Portal 2 (ID 2) / projects: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_PROJECTS\_COVERAGE\]
- Portal 2 (ID 2) / projects: Additional-field count is unknown; the documented total limit is 110. Target edition and per-type mapping still require confirmation. \[portal:2:FIELD\_PROJECTS\_CAPACITY\]
- Portal 2 (ID 2) / releases: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_RELEASES\_COVERAGE\]
- Portal 2 (ID 2) / releases: 1 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:2:FIELD\_RELEASES\_CAPACITY\]
- Portal 2 (ID 2) / users: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_USERS\_COVERAGE\]
- Portal 2 (ID 2) / users: 1 distinct additional fields observed; the documented total limit is 50. Target edition and per-type mapping still require confirmation. \[portal:2:FIELD\_USERS\_CAPACITY\]
- Portal 2 (ID 2) / technicians: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_TECHNICIANS\_COVERAGE\]
- Portal 2 (ID 2) / technicians: Additional-field count is unknown; the documented total limit is 50. Target edition and per-type mapping still require confirmation. \[portal:2:FIELD\_TECHNICIANS\_CAPACITY\]
- Portal 2 (ID 2) / assets: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: PARTIAL. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_ASSETS\_COVERAGE\]
- Portal 2 (ID 2) / assets: 2 distinct additional fields observed; the documented total limit is 100. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. \[portal:2:FIELD\_ASSETS\_CAPACITY\]
- Portal 2 (ID 2) / computers: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_COMPUTERS\_COVERAGE\]
- Portal 2 (ID 2) / computers: 2 distinct additional fields observed; the documented total limit is 52. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. \[portal:2:FIELD\_COMPUTERS\_CAPACITY\]
- Portal 2 (ID 2) / cis: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_CIS\_COVERAGE\]
- Portal 2 (ID 2) / cis: 1 distinct additional fields observed; the documented total limit is 1560. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. \[portal:2:FIELD\_CIS\_CAPACITY\]
- Portal 2 (ID 2) / contracts: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_CONTRACTS\_COVERAGE\]
- Portal 2 (ID 2) / contracts: Additional-field count is unknown; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:2:FIELD\_CONTRACTS\_CAPACITY\]
- Portal 2 (ID 2) / purchases: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_PURCHASES\_COVERAGE\]
- Portal 2 (ID 2) / purchases: Additional-field count is unknown; the documented total limit is 164. Target edition and per-type mapping still require confirmation. \[portal:2:FIELD\_PURCHASES\_CAPACITY\]
- Portal 3 (ID 3) / requests: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_REQUESTS\_COVERAGE\]
- Portal 3 (ID 3) / requests: 1 distinct additional fields observed; the documented total limit is 250. Target edition and per-type mapping still require confirmation. \[portal:3:FIELD\_REQUESTS\_CAPACITY\]
- Portal 3 (ID 3) / problems: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_PROBLEMS\_COVERAGE\]
- Portal 3 (ID 3) / problems: 1 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:3:FIELD\_PROBLEMS\_CAPACITY\]
- Portal 3 (ID 3) / changes: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_CHANGES\_COVERAGE\]
- Portal 3 (ID 3) / changes: 2 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:3:FIELD\_CHANGES\_CAPACITY\]
- Portal 3 (ID 3) / projects: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_PROJECTS\_COVERAGE\]
- Portal 3 (ID 3) / projects: 1 distinct additional fields observed; the documented total limit is 110. Target edition and per-type mapping still require confirmation. \[portal:3:FIELD\_PROJECTS\_CAPACITY\]
- Portal 3 (ID 3) / releases: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_RELEASES\_COVERAGE\]
- Portal 3 (ID 3) / releases: Additional-field count is unknown; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:3:FIELD\_RELEASES\_CAPACITY\]
- Portal 3 (ID 3) / users: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_USERS\_COVERAGE\]
- Portal 3 (ID 3) / users: 1 distinct additional fields observed; the documented total limit is 50. Target edition and per-type mapping still require confirmation. \[portal:3:FIELD\_USERS\_CAPACITY\]
- Portal 3 (ID 3) / technicians: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_TECHNICIANS\_COVERAGE\]
- Portal 3 (ID 3) / technicians: Additional-field count is unknown; the documented total limit is 50. Target edition and per-type mapping still require confirmation. \[portal:3:FIELD\_TECHNICIANS\_CAPACITY\]
- Portal 3 (ID 3) / assets: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_ASSETS\_COVERAGE\]
- Portal 3 (ID 3) / assets: 2 distinct additional fields observed; the documented total limit is 100. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. \[portal:3:FIELD\_ASSETS\_CAPACITY\]
- Portal 3 (ID 3) / computers: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_COMPUTERS\_COVERAGE\]
- Portal 3 (ID 3) / computers: 2 distinct additional fields observed; the documented total limit is 52. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. \[portal:3:FIELD\_COMPUTERS\_CAPACITY\]
- Portal 3 (ID 3) / cis: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_CIS\_COVERAGE\]
- Portal 3 (ID 3) / cis: 1 distinct additional fields observed; the documented total limit is 1560. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. \[portal:3:FIELD\_CIS\_CAPACITY\]
- Portal 3 (ID 3) / contracts: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_CONTRACTS\_COVERAGE\]
- Portal 3 (ID 3) / contracts: Additional-field count is unknown; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:3:FIELD\_CONTRACTS\_CAPACITY\]
- Portal 3 (ID 3) / purchases: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_PURCHASES\_COVERAGE\]
- Portal 3 (ID 3) / purchases: Additional-field count is unknown; the documented total limit is 164. Target edition and per-type mapping still require confirmation. \[portal:3:FIELD\_PURCHASES\_CAPACITY\]
- Portal 4 (ID 4) / requests: 0 distinct request-field definitions observed; 0 have recognized types. The combined paid-tier limit is 250. \[portal:4:REQUEST\_FIELD\_CAPACITY\]
- Portal 4 (ID 4) / requests: No matching issue established from 0 checked records; collection or required-field coverage is incomplete. \[portal:4:FIELD\_NAME\_COLLISIONS\]
- Portal 4 (ID 4) / requests: 0 typed values checked; definitions, defaults, options, and uninspected record values may add exposure. \[portal:4:FIELD\_VALUE\_LENGTHS\]

#### Target-cloud unknowns

- Target reconciliation, permissions, workflow execution, recovery and migration success are not validated by this scan.

#### Vendor confirmation required

- Agree evidence requirements and exception handling for every unresolved migration difference.

#### Project/business decision required

- Approve go/no-go thresholds and accountable owners; resolve or explicitly accept each blocker before cutover.
