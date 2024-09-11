# Test Workflow with ArgoCD

This folder contains k6, Playwright and Postman test workflows which automates running respective tests in your environment. We will use this repo as part of and ArgoCD application.

## Folder Contents

- `basic-k6.yaml`: k6 test workflow file for load testing.
- `basic-playwright.yaml`: Playwright test workflow file for functional tests.
- `basic-postman.yaml`: Postman test workflow file for API tests.

## Prerequisites

Before setting up the workflow, ensure you have the following:

- ArgoCD installed and configured in your Kubernetes cluster.
- Testkube installed and configured in your Kubernetes cluster.

## Steps to Configure

Follow these steps to set up and configure the K6 test workflow with ArgoCD:

1. Clone this repository to your local machine.
2. Create a new ArgoCD application for all the test workflow - *this allows ArgoCD to track the yaml files and deploy the workflows to your Kubernetes cluster*.
3. After the application is created, sync it with your repository to deploy the workflow.
4. Monitor the deployment using ArgoCD’s web UI or CLI.
5. Once the workflow is deployed, you can trigger the test workflow using testkube cli or dashboard.
