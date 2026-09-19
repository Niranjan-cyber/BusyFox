# BusyFox

## Live deployments

| What | URL | Region |
|---|---|---|
| Frontend (Amplify Hosting, app `dw3gwg5t169l9`, branch `main`) | https://main.dw3gwg5t169l9.amplifyapp.com/ | eu-north-1 |
| API Gateway (Task 6 skeleton, stack `opportunity-engine-skeleton`) | https://vx59qs2osl.execute-api.eu-north-1.amazonaws.com/ | eu-north-1 |

The Amplify app is git-connected to `main` with auto-build enabled, so every push to `main` redeploys the frontend from `amplify.yml`. `VITE_API_BASE_URL` is set as an Amplify app-level environment variable (`https://vx59qs2osl.execute-api.eu-north-1.amazonaws.com`, no trailing slash) as of 2026-09-20 — the deployed frontend hits the live API and only falls back to `DEMO FIXTURE` on a real failure, never silently. Changing this value requires a manual redeploy of the branch (Amplify Console → Hosting → `main` → latest job → Redeploy this version) — a new env var alone does not trigger a build.

## Deploy the Task 6 skeleton

`scripts/task6-deploy-wizard.sh` walks through AWS CLI/SAM CLI setup, credentials, confirming Bedrock model access, and `sam deploy` for `infra/api-gateway.yaml`. Run it from a bash shell (Git Bash on Windows): `bash scripts/task6-deploy-wizard.sh`.