# Review HTML Pack Design

## Purpose

Brand Marketing Knowledge Compiler produces multiple Markdown files. They are useful as AI-readable marketing semantic bases, but they are not a good primary review surface for brand managers.

The first-phase workflow should add a lightweight local review pack:

```text
review/
├── brand_review.html
└── review_decisions.json
```

This is not a web app, SaaS product, backend service, or enterprise approval system.

## Scope

In scope:

- Generate `review/brand_review.html` from first-phase Markdown outputs.
- Present key review items in one local HTML page.
- Highlight high-risk strategy, data, claim, compliance, competitor, and external-publication issues.
- Show source anchors such as `S001#page=24`.
- Allow browser-side review states: confirm, needs edit, needs supplement, reject.
- Let the user download or copy `review_decisions.json`.

Out of scope:

- No model API.
- No backend.
- No auth.
- No database.
- No multi-user workflow.
- No full React/Vite app.
- No automatic confirmed Markdown generation in the first version.

## Review Sections

The HTML should include:

1. Overview.
2. Document Profile Review from `02_document_profile.md`.
3. Key Facts / Claims Review from `04_key_facts_and_claims.md`.
4. Strategy and Execution Review from `05_strategy_and_execution_map.md`.
5. Risk and Review Items from `06_risk_and_review_items.md` and `09_quality_check_report.md`.

Product SKU / fragrance review is optional and should appear only when the document profile indicates a product-training or product-claim document.

## CLI

Add:

```bash
brand-skill build-review-pack <project_dir>
```

Expected behavior:

- Reads `outputs/`.
- Creates `review/`.
- Writes `review/brand_review.html`.
- Fails clearly if required default outputs are missing.
- Does not overwrite existing `review_decisions.json`.

## Testing

Add tests that verify:

- `build-review-pack` creates `review/brand_review.html`.
- The HTML includes Document Profile, Key Facts / Claims, Strategy and Execution, and Risk Review sections.
- Missing required outputs fail clearly.
- Existing tests continue to pass.
