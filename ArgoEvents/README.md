# Test Workflow webhook trigger with Argo Events

This folder contains k6 test workflow which automates running test in your environment and Argo Events configurations needed for integrating it with Testkube.

## Folder Contents

- `configmap-k6.yaml`: k6 test workflow file for load testing.
- `argo-events-sa.yaml`: Service Account with RBAC settings.
- `sample-configmap.yaml`: ConfigMap to monitor for changes.
- `configmap-eventsource.yaml`: EventSource that checks for ConfigMap in the default namespace and has label watch: “true” for events ADD, UPDATE, and DELETE.
- `webhook-sensor.yaml`: Sensor to connect to EventSource and Testkube webhook.

## Prerequisites

Before setting up the workflow, ensure you have the following:

- Argo Events [installed](https://argoproj.github.io/argo-events/quick_start/) and configured in your Kubernetes cluster with Validating Admission Controller and Event Bus.
- Testkube [installed](https://docs.testkube.io/articles/install/multi-agent) and configured in your Kubernetes cluster.
