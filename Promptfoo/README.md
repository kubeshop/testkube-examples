# Promptfoo: Application Red-Team Testing with FinBuddy

Red-team a deployed LLM application using Promptfoo + Testkube. This demo catches vulnerabilities in the app layer (system prompt, guardrails) that the model layer alone won't catch.

## What is this demo?

- **The app**: FinBuddy, a ~60-line FastAPI chatbot wrapper with a system prompt and one guardrail (no investment advice, no prompt leakage).
- **The goal**: Red-team FinBuddy against four attack categories.
- **The tools**: Promptfoo for attack generation + grading, Testkube for orchestration + artifact storage.
- **Why it matters**: Models can pass safety benchmarks but still leak instructions or drop guardrails at the app layer.

## Folder structure

- `app/` — FastAPI application + Dockerfile + K8s Deployment
- `testkube/` — TestWorkflow orchestration YAML
- `promptfoo/` — Red-team scan config + execution output

## Prerequisites

- Kubernetes cluster with Testkube installed
- OpenAI API key (`$OPENAI_API_KEY`)
- kubectl configured and authenticated

## Run on cluster with Testkube

### 1. Deploy the app

```bash
# Build image
docker build -t finbuddy:latest app/

# Create secret for OpenAI API key
kubectl create secret generic openai-api-key \
  --from-literal=OPENAI_API_KEY=$OPENAI_API_KEY \
  -n default \
  --dry-run=client -o yaml | kubectl apply -f -

# Deploy FinBuddy
kubectl apply -f app/deployment.yaml
```

### 2. Deploy the red-team TestWorkflow

```bash
kubectl apply -f testkube/testworkflow.yaml
testkube run testworkflow layer4-finbuddy-redteam -f
```

The workflow:
- Installs Promptfoo in a container
- Runs the red-team scan against the deployed FinBuddy endpoint
- Generates `report.json` as artifact
- Parses results and fails if any attack succeeded

### 3. View results

Results appear in the Testkube dashboard that can be downloaded:
- **report.json** — parseable, structured attack results

## The vulnerability categories

| Category | Checks |
|----------|--------|
| Prompt injection | Can an attacker override the system prompt? |
| Jailbreak | Can roleplay/DAN-style framing drop the guardrail? |
| System prompt leakage | Can the app be tricked into revealing instructions? |
| Policy violation | Does it ever give specific buy/sell/hold advice? |

## Output example

After running the TestWorkflow, `promptfoo/report.json` contains:
```json
{
  "results": [
    {
      "category": "prompt-injection",
      "status": "PASS",
      "attacks": [...]
    },
    ...
  ]
}
```

Testkube stores the full report as a downloadable artifact.
