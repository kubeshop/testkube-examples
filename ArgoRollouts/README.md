# Testkube with ArgoRollouts

## Overview

This project integrates Testkube with ArgoRollouts to provide a robust testing and deployment pipeline. Testkube is a cloud-native testing framework, while ArgoRollouts is a Kubernetes controller for managing the deployment of applications using advanced deployment strategies.

## Prerequisites

- Kubernetes cluster
- kubectl configured to interact with your cluster
- Testkube installed
- ArgoRollouts installed
- API key from http://api.weatherapi.com

## Project Structure

- `rollout.yaml`: Configuration file for deploying the application using ArgoRollouts.
- `template.yaml`: Template file containing the Testkube Test Workflow and other configurations.
- `weatherSample-v1`: Files for the v1 of the weather application which shows the weather of Hyderabad.
- `weatherSample-v2`: Files for the v1 of the weather application which shows the weather of New York.
  