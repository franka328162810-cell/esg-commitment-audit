# Publishing to GitHub

The v0.2.0 repository is prepared for a new public GitHub repository named
`esg-commitment-audit`.

## Before publishing

1. Confirm `git status --short --ignored`.
2. Confirm the following paths remain ignored:
   - `_audit_inputs/`
   - `_audit_inputs_utf8/`
   - `_audit_reports/`
   - `audit-output/`
   - `dist*/`
   - `.esg-commitment-audit-service/`
3. Confirm no unpublished manuscript, customer report, API key, or credential is
   present in the tracked files.
4. Review `LICENSE`, `NOTICE`, `README.md`, and `docs/RELEASE_CHECK.md`.

## Create the first commit

Run from the repository root after reviewing the exact file list:

```powershell
git add .codex-plugin .env.example .github .gitignore .mcp.json CHANGELOG.md LICENSE NOTICE README.md assets docs examples formalizations pyproject.toml skills src tests validation
git status --short
git commit -m "release: ESG commitment audit workbench v0.2.0"
```

Do not use `git add .` until the ignored-path check above has passed.

## Add the GitHub remote

Create an empty public repository named `esg-commitment-audit` under the target
account, then:

```powershell
git remote add origin https://github.com/franka328162810-cell/esg-commitment-audit.git
git push -u origin master
```

Do not create a README, LICENSE, or `.gitignore` in GitHub's new-repository
screen because those files already exist locally.

## Publishing boundary

The source code and reference rules are Apache 2.0. Academic use remains free.
Future formalizations under `formalizations/` are intended for CC BY-SA 4.0.
Commercial hosted operation, support, private deployment, certifications, and
enterprise integration remain separate paid services.

The repository root is also the Codex plugin root. Confirm that
`.codex-plugin/plugin.json`, `.mcp.json`, `skills/`, and `assets/icon.svg` are
included in the release before marketplace submission.
