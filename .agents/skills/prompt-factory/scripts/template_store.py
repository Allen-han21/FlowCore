#!/usr/bin/env python3
"""Template definitions for workflow-prompt-factory."""

COMMON_BLOCKS = {
    "COMMON_USE": """Use:
- AGENTS.md
- existing repository patterns
- current project architecture""",
    "COMMON_DISCOVER_RULES": """Discovery rules:
- do not implement code
- do not modify files
- do not create final architecture plan yet
- do not infer missing requirements as confirmed facts
- separate confirmed facts vs inferred assumptions
- list open questions explicitly""",
    "COMMON_NO_RUN": """Do not run:
- builds
- compile checks
- tests
- simulators
- xcodebuild
- fastlane
- pod install
- bundle install
- dependency installation
- runtime commands""",
    "COMMON_IMPLEMENT_RULES": """Rules:
- keep changes minimal
- no unrelated refactors
- do not redesign architecture
- do not expand scope
- preserve existing patterns
- modify only planned files unless strictly required
- preserve stacked PR integrity if applicable
- preserve UIKit-only direction if applicable""",
    "COMMON_REVIEW_CLASSIFICATION": """Classify findings:
- BLOCKING
- SHOULD FIX
- OPTIONAL""",
    "COMMON_ADVISORY_CLASSIFICATION": """Classify findings:
- SHOULD FIX
- OPTIONAL

Do not use BLOCKING.""",
}

TEMPLATES = {
    "discover.general": {
        "stage": "discover",
        "required_vars": ["task"],
        "body": """Create ai/discovery.md in Korean.

Task:
- {{task}}

Act as discovery analyst only.

{{COMMON_USE}}
{{COMMON_DISCOVER_RULES}}
{{COMMON_NO_RUN}}

Investigate:
1. request summary
2. confirmed facts from repository context
3. inferred assumptions (label as assumptions)
4. open questions before specification/planning
5. existing architecture map related to task
6. related code paths
7. existing similar patterns
8. runtime/lifecycle flow related to task
9. risk areas (runtime, regression, data consistency)
10. scope boundary (in-scope / out-of-scope)
11. candidate files to inspect next
12. recommended next step (spec or direct plan) with rationale

Output format in ai/discovery.md:
## 1. Request Summary
## 2. Confirmed Facts
## 3. Inferred Assumptions
## 4. Open Questions
## 5. Existing Architecture Map
## 6. Related Code Paths
## 7. Existing Similar Patterns
## 8. Runtime Flow
## 9. Risk Areas
## 10. Scope Boundary
## 11. Candidate Files
## 12. Recommended Next Step
""",
    },
    "discover.ios-cache": {
        "stage": "discover",
        "required_vars": ["task"],
        "body": """Create ai/discovery.md in Korean.

Task:
- {{task}}

Act as discovery analyst only for iOS networking/cache context.

{{COMMON_USE}}
{{COMMON_DISCOVER_RULES}}
{{COMMON_NO_RUN}}

Investigate:
1. current networking layer and boundaries
2. URLSession / Alamofire / Moya / Rx networking usage
3. existing cache policy and cache invalidation behavior
4. existing offline handling and retry/fallback flow
5. repository/service-level error handling behavior
6. screens or user flows likely affected
7. whether URLCache is already configured and where
8. whether target API responses are cacheable
9. stale data risk and consistency risk
10. security/privacy risk around cached payloads
11. candidate files to inspect next
12. open questions required before spec/plan

Output format in ai/discovery.md:
## 1. Request Summary
## 2. Confirmed Facts
## 3. Inferred Assumptions
## 4. Open Questions
## 5. Existing Architecture Map
## 6. Related Code Paths
## 7. Existing Similar Patterns
## 8. Runtime Flow
## 9. Risk Areas
## 10. Scope Boundary
## 11. Candidate Files
## 12. Recommended Next Step
""",
    },
    "spec.from-discovery": {
        "stage": "spec",
        "required_vars": ["task"],
        "body": """Create ai/spec.md in Korean based on ai/discovery.md.

Task:
- {{task}}

Read:
- ai/discovery.md
- AGENTS.md
- existing repository patterns

Act as spec author only.

Do not implement code.
Do not modify product/source files.
Do not create implementation plan in this step.
{{COMMON_NO_RUN}}

The spec must include:
1. problem statement
2. goals
3. non-goals
4. target user/runtime scenarios
5. functional requirements
6. non-functional requirements
7. constraints and assumptions
8. acceptance criteria
9. validation approach (human/runtime)
10. unresolved questions to settle before planning

If ai/discovery.md has unresolved blockers, keep them explicit.
Do not fill missing facts with speculation.""",
    },
    "plan.from-discovery": {
        "stage": "plan",
        "required_vars": ["task"],
        "body": """Create ai/plan.md.

Task:
- {{task}}

Read first:
- ai/discovery.md
- ai/spec.md if present
- AGENTS.md
- existing repository patterns

Act as architect only.

Do not implement code.
Do not modify files.
{{COMMON_NO_RUN}}

Use discovery/spec as the source of truth for scope.

The plan must include:
1. problem summary
2. root cause analysis
3. files to inspect
4. files to modify
5. implementation steps
6. edge cases
7. test strategy
8. runtime validation steps
9. risks
10. rollback considerations
11. open questions carried from discovery/spec

Keep the scope minimal.
Avoid unnecessary refactoring.
Preserve existing architecture.""",
    },
    "plan.feature": {
        "stage": "plan",
        "required_vars": ["task"],
        "body": """Create ai/plan.md.

Task:
- {{task}}

Act as architect only.

{{COMMON_USE}}

Do not implement code.

The plan must include:
1. problem summary
2. root cause analysis
3. files to inspect
4. files to modify
5. implementation steps
6. edge cases
7. test strategy
8. runtime validation steps
9. risks
10. rollback considerations

Keep the scope minimal.
Avoid unnecessary refactoring.
Preserve existing architecture.""",
    },
    "plan.bug": {
        "stage": "plan",
        "required_vars": ["task"],
        "body": """Create ai/plan.md.

Task:
- {{task}}

Act as architect only.

{{COMMON_USE}}
- existing reaction workflow and stacked PR structure if relevant

Do not implement code.

The plan must include:
1. bug summary
2. expected behavior
3. current behavior
4. reproduction conditions
5. suspected root cause
6. affected runtime flow
7. files to inspect
8. files likely to modify
9. minimal fix strategy
10. regression risk analysis
11. edge cases
12. test strategy
13. runtime validation steps
14. rollback considerations

Focus on:
- minimal blast radius
- preserving existing architecture
- preventing regression
- preserving stacked PR integrity if applicable
- preserving UIKit-only direction if applicable

Avoid:
- unnecessary refactoring
- architecture redesign
- speculative optimization
- scope expansion""",
    },
    "plan.crash": {
        "stage": "plan",
        "required_vars": ["crash_symptom"],
        "body": """Create ai/plan.md.

Task:
- {{crash_symptom}}
- {{crash_context}}

Act as architect only.

{{COMMON_USE}}
- existing reaction workflow and stacked PR structure if relevant

Do not implement code.

The plan must include:
1. crash summary
2. expected behavior
3. actual crash behavior
4. reproduction conditions
5. crash log / stack trace interpretation
6. suspected crash root cause
7. affected runtime flow
8. affected thread / lifecycle timing if relevant
9. nilability / force unwrap / optional handling risk
10. files to inspect
11. files likely to modify
12. minimal crash fix strategy
13. regression risk analysis
14. edge cases
15. test strategy
16. runtime validation steps
17. rollback considerations

Focus on:
- preventing the crash with minimal blast radius
- fixing the root cause, not only hiding the symptom
- preserving existing runtime behavior outside the crash path""",
    },
    "plan.build-failure": {
        "stage": "plan",
        "required_vars": ["build_error"],
        "body": """Analyze the build failure for current PR.

Read:
- ai/pr-split-plan.md
- ai/review.md
- current git diff

Build error:
- {{build_error}}

Task:
Identify the root cause and propose the minimal fix.

Rules:
- do not modify code
- do not run builds/tests
- preserve current PR scope
- avoid refactoring

Output in Korean:
1. root cause
2. affected files
3. whether this belongs to current PR scope
4. minimal fix plan
5. risk""",
    },
    "plan.pr-split": {
        "stage": "plan",
        "required_vars": ["task", "context"],
        "body": """Create ai/pr-split-plan.md.

Task:
- {{task}}

Context:
- {{context}}

Act as architect and release planner only.

{{COMMON_USE}}
- current git history
- current branch diff

Do not modify code.
Do not rebase.
Do not commit.
Do not push.
{{COMMON_NO_RUN}}

The plan must include:
1. summary of total change scope
2. proposed PR breakdown
3. purpose of each PR
4. files likely included in each PR
5. dependency order between PRs
6. commits likely belonging to each PR if identifiable
7. changes that should be excluded or postponed
8. minimal refactoring recommendations
9. risks per PR
10. recommended branch strategy
11. recommended review order
12. rollback considerations""",
    },
    "plan.ui-sequential": {
        "stage": "plan",
        "required_vars": ["task", "items"],
        "body": """Create ai/plan.md.

Task:
- {{task}}

Items:
{{items}}

Context:
- one item per cycle (설계 → 구현 → 리뷰 → 런타임 확인 → 커밋)

Act as architect and workflow planner only.

{{COMMON_USE}}
- existing reaction workflow and stacked PR structure if relevant

Do not implement code.
Do not modify files.
{{COMMON_NO_RUN}}

The plan must include:
1. 전체 목표 요약
2. 항목 목록
3. 항목별 수정 범위
4. 항목별 files to inspect
5. 항목별 files likely to modify
6. 항목별 implementation strategy
7. 항목별 runtime validation steps
8. 항목별 regression risk
9. 항목별 commit message proposal
10. 권장 순서
11. 항목 간 의존성
12. 한 커밋에 섞이면 안 되는 항목
13. 보류/확인 필요 항목""",
    },
    "plan.bug-ui": {
        "stage": "plan",
        "required_vars": ["task", "items", "base_branch", "working_branch"],
        "body": """Create ai/plan.md.

Task:
- {{task}}

Items:
{{items}}

Context:
- Base branch: {{base_branch}}
- Working branch: {{working_branch}}
- one item per cycle
- one item per commit

Act as architect and workflow planner only.

{{COMMON_USE}}
- existing reaction workflow and stacked PR structure if relevant

Do not implement code.
Do not modify files.
{{COMMON_NO_RUN}}

The plan must include:
1. 전체 수정 목표 요약
2. 제공된 수정 항목 목록
3. 명시되지 않은 항목에 대한 확인 필요 사항
4. 각 항목별 예상 수정 범위
5. 각 항목별 files to inspect
6. 각 항목별 files likely to modify
7. 각 항목별 implementation strategy
8. 각 항목별 runtime validation steps
9. 각 항목별 regression risk
10. 각 항목별 commit message proposal
11. 권장 작업 순서
12. 항목 간 의존성
13. 한 커밋에 섞이면 안 되는 항목
14. 보류/확인 필요 항목""",
    },
    "plan.redesign": {
        "stage": "plan",
        "required_vars": ["task", "items", "context"],
        "body": """Create ai/plan.md.

Task:
- {{task}}

Items:
{{items}}

Context:
- {{context}}

Act as architect only.

{{COMMON_USE}}
- existing reaction workflow
- previous implementation diff if available
- ai/review.md if relevant
- ai/gemini-review.md if relevant

Do not implement code.
Do not modify files.
{{COMMON_NO_RUN}}

The plan must include:
1. redesign summary
2. why the previous approach likely failed
3. expected behavior
4. current behavior
5. affected runtime flow
6. affected state/update/rendering flow
7. performance-sensitive points
8. files to inspect
9. files likely to modify
10. minimal redesigned fix strategy
11. rejected approaches and why
12. implementation steps
13. runtime validation steps
14. regression risk analysis
15. edge cases
16. rollback considerations
17. commit boundary per item""",
    },
    "implement.feature": {
        "stage": "implement",
        "required_vars": ["task"],
        "body": """Read ai/plan.md and implement exactly.

Task:
- {{task}}

Use:
- AGENTS.md
- .claude/rules
- existing repository conventions

{{COMMON_IMPLEMENT_RULES}}

Requirements:
- update/add tests if needed
- summarize changed files
- explain any deviation from ai/plan.md

{{COMMON_NO_RUN}}

Human will perform runtime/build validation manually.
Stop after implementation.
Do not perform review.""",
    },
    "implement.bug": {
        "stage": "implement",
        "required_vars": [],
        "body": """Read ai/plan.md and implement the bug fix exactly.

Use:
- AGENTS.md
- .claude/rules
- existing repository conventions

{{COMMON_IMPLEMENT_RULES}}
- fix only the bug described in ai/plan.md
- address the suspected root cause from ai/plan.md

Requirements:
- summarize changed files
- explain any deviation from ai/plan.md
- explain why the fix remains minimal and safe

{{COMMON_NO_RUN}}

Human performs runtime/build validation separately.
Stop after implementation.
Do not perform review.""",
    },
    "implement.crash": {
        "stage": "implement",
        "required_vars": [],
        "body": """Read:
- ai/plan.md
- AGENTS.md
- .claude/rules

Task:
Implement the crash fix exactly according to ai/plan.md.

{{COMMON_IMPLEMENT_RULES}}
- fix only the crash described in ai/plan.md
- address the suspected crash root cause
- preserve existing runtime behavior outside the crash path

Focus on:
- nilability / optional safety
- lifecycle timing safety
- thread/main-thread safety if relevant
- async callback/race-condition safety if relevant
- Objective-C / Swift bridging safety if relevant

{{COMMON_NO_RUN}}

After implementation:
- summarize changed files
- explain the crash root cause addressed
- explain why the fix is minimal and safe
- list any deviation from ai/plan.md
- stop after implementation
- do not perform review""",
    },
    "implement.ui-sequential": {
        "stage": "implement",
        "required_vars": ["current_item"],
        "body": """Read:
- ai/plan.md
- AGENTS.md
- .claude/rules

Task:
Implement only the current UI guide item from ai/plan.md.

Current item:
- {{current_item}}

{{COMMON_IMPLEMENT_RULES}}
- implement only the current item
- do not implement future items
- avoid broad visual cleanup

Do not perform review/commit/push/merge.
{{COMMON_NO_RUN}}

Human performs runtime/build validation separately.

After implementation:
- summarize changed files
- explain which UI guide item was implemented
- explain why the change scope remained minimal
- list potential runtime/layout risks
- stop after implementation""",
    },
    "implement.redesign": {
        "stage": "implement",
        "required_vars": ["current_item"],
        "body": """Read:
- ai/plan.md
- AGENTS.md
- ai/review.md if relevant

Task:
Implement the redesigned fix exactly according to ai/plan.md.

Current item:
- {{current_item}}

{{COMMON_IMPLEMENT_RULES}}
- implement only the current failed item
- do not touch already completed items
- do not combine multiple failed items into one implementation

Focus on:
- cell reuse safety
- rendering timing
- stale state prevention
- unnecessary reload/layout invalidation prevention
- scroll performance

Do not perform review/commit/push/merge.
{{COMMON_NO_RUN}}

After implementation:
- summarize changed files
- explain the runtime issue addressed
- explain why the fix is minimal
- list remaining validation points for Human
- stop after implementation""",
    },
    "review.feature": {
        "stage": "review",
        "required_vars": [],
        "body": """Review current git diff against ai/plan.md.
Write ai/review.md in Korean.

Review responsibilities:
- detect architecture drift
- detect unintended side effects
- detect unnecessary complexity
- verify repository conventions
- verify scope discipline
- verify test coverage adequacy

{{COMMON_REVIEW_CLASSIFICATION}}

Focus on:
- correctness
- maintainability
- runtime risk
- implementation consistency

Do not rewrite implementation unless critical.""",
    },
    "review.bug": {
        "stage": "review",
        "required_vars": [],
        "body": """Review current git diff against ai/plan.md.
Write ai/review.md in Korean.

Review responsibilities:
- verify the bug root cause from ai/plan.md is actually addressed
- verify regression risk and minimal blast radius
- verify no unrelated refactors or scope expansion
- verify runtime behavior outside target path is preserved

{{COMMON_REVIEW_CLASSIFICATION}}

{{COMMON_NO_RUN}}

Human performs runtime/build validation separately.""",
    },
    "review.crash": {
        "stage": "review",
        "required_vars": [],
        "body": """Review current git diff against ai/plan.md.
Write ai/review.md in Korean.

Review responsibilities:
- verify actual crash root cause is addressed
- detect crash masking or symptom-only fixes
- verify lifecycle/thread/async safety
- verify minimal blast radius

{{COMMON_REVIEW_CLASSIFICATION}}

{{COMMON_NO_RUN}}

Human performs runtime/build validation separately.""",
    },
    "advisory.general": {
        "stage": "advisory",
        "required_vars": [],
        "body": """Perform advisory review only.

Context:
- Codex is the primary reviewer and architecture authority.
- Your role is secondary/advisory review only.

Review current git diff and existing review artifacts.

Focus on:
- edge cases
- regression risks
- hidden assumptions
- runtime inconsistencies
- missing validation paths
- overlooked error handling

Write findings to ai/gemini-review.md in Korean.

{{COMMON_ADVISORY_CLASSIFICATION}}

Do not rewrite implementation.
Do not run commands.""",
    },
    "reconcile.general": {
        "stage": "reconcile",
        "required_vars": [],
        "body": """Review ai/gemini-review.md and determine which comments are actionable.
Append final reconciliation decisions to ai/review.md.

Rules:
- Codex remains the final review authority.
- Gemini feedback is advisory only.
- preserve approved architecture and minimal fix scope
- reject speculative fixes or broad cleanup unless critical

Classify Gemini comments as:
- ACCEPTED
- REJECTED
- OPTIONAL

For each decision:
- explain why the comment is or is not actionable
- explain runtime/regression implications where relevant""",
    },
    "rereview.general": {
        "stage": "rereview",
        "required_vars": [],
        "body": """Re-review current git diff against:
- ai/plan.md
- ai/review.md
- ai/gemini-review.md

Focus only on:
- whether accepted review feedback was correctly addressed
- whether new regressions or scope expansion were introduced
- whether BLOCKING issues remain

Update ai/review.md with the final status.
Write in Korean.
Do not rewrite implementation.
{{COMMON_NO_RUN}}""",
    },
    "git.commit": {
        "stage": "git",
        "required_vars": ["base_branch", "new_branch", "ticket"],
        "body": """Read:
- ai/plan.md
- ai/review.md
- ai/gemini-review.md

Task:
Prepare final bug-fix PR branch.

Base branch:
{{base_branch}}

New PR branch:
{{new_branch}}

Before commit:
- verify current diff is limited to approved scope
- verify no unrelated files are included
- verify no ai/.ai/.codex/.claude/.gemini/.superset files are staged

Do:
- create/switch branch if needed
- show git status
- show git diff --stat
- stage only intended product/source changes
- commit changes

Commit message:
[{{ticket}}] fix(logic): {{commit_subject}}

Do not push/create PR/merge.
{{COMMON_NO_RUN}}

After commit:
- show commit summary
- show changed file list
- explain committed scope""",
    },
}
