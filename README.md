# BusyFox

## Live deployments

| What | URL | Region |
|---|---|---|
| Frontend (Amplify Hosting, app `dw3gwg5t169l9`, branch `main`) | https://main.dw3gwg5t169l9.amplifyapp.com/ | eu-north-1 |
| API Gateway (Task 6 skeleton, stack `opportunity-engine-skeleton`) | https://vx59qs2osl.execute-api.eu-north-1.amazonaws.com/ | eu-north-1 |

The Amplify app is git-connected to `main` with auto-build enabled, so every push to `main` redeploys the frontend from `amplify.yml`. `VITE_API_BASE_URL` is not yet set as an Amplify environment variable, so the deployed frontend currently serves fixture data (`DEMO FIXTURE`, per the resilience ladder) rather than hitting the API Gateway above — wire that once Task 20/21 land real data.

## Deploy the Task 6 skeleton

`scripts/task6-deploy-wizard.sh` walks through AWS CLI/SAM CLI setup, credentials, confirming Bedrock model access, and `sam deploy` for `infra/api-gateway.yaml`. Run it from a bash shell (Git Bash on Windows): `bash scripts/task6-deploy-wizard.sh`.