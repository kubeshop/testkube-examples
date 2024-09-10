# K6 Test Workflow with ArgoCD

This folder contains a K6 test workflow file, `basic-k6.yaml` which automates running K6 load tests in your environment. We will use this repo as part of and ArgoCD application.

## Folder Contents

- `basic-k6.yaml`: The K6 test workflow file for aload testing.

## Prerequisites

Before setting up the workflow, ensure you have the following:

- ArgoCD installed and configured in your Kubernetes cluster.
- Testkube installed and configured in your Kubernetes cluster.

## Steps to Configure

Follow these steps to set up and configure the K6 test workflow with ArgoCD:

1. Clone this repository to your local machine.
2. Create a new ArgoCD application for the K6 test workflow - *this allows ArgoCD to track the test.yaml file and deploy the workflow to your Kubernetes cluster*.
3. After the application is created, sync it with your repository to deploy the workflow.
4. Monitor the deployment using ArgoCD’s web UI or CLI.
5. Once the workflow is deployed, you can trigger the test workflow using testkube cli or dashboard.
