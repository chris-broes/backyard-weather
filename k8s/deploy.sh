#!/usr/bin/env bash
# Deploy LedgerLine to a GKE cluster.
#
# Prerequisites:
#   gcloud auth login && gcloud auth configure-docker REGION-docker.pkg.dev
#   gcloud container clusters get-credentials CLUSTER_NAME --region REGION --project PROJECT_ID
#
# Usage:
#   export PROJECT_ID=my-gcp-project
#   export REGION=us-central1
#   export IMAGE_TAG=latest        # or a git SHA
#   ./k8s/deploy.sh

set -euo pipefail

: "${PROJECT_ID:?Set PROJECT_ID}"
: "${REGION:?Set REGION}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
REGISTRY="${REGION}-docker.pkg.dev/${PROJECT_ID}/ledgerline"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== Building and pushing images ==="

docker build -t "${REGISTRY}/ledger:${IMAGE_TAG}" "${REPO_ROOT}"
docker build -t "${REGISTRY}/reminders:${IMAGE_TAG}" "${REPO_ROOT}/reminders"
docker build -t "${REGISTRY}/recommendations:${IMAGE_TAG}" "${REPO_ROOT}/recommendations"

docker push "${REGISTRY}/ledger:${IMAGE_TAG}"
docker push "${REGISTRY}/reminders:${IMAGE_TAG}"
docker push "${REGISTRY}/recommendations:${IMAGE_TAG}"

echo "=== Substituting image tags in manifests ==="

for SVC in ledger reminders recommendations; do
    sed -i.bak \
        "s|REGION-docker.pkg.dev/PROJECT_ID/ledgerline/${SVC}:latest|${REGISTRY}/${SVC}:${IMAGE_TAG}|g" \
        "${REPO_ROOT}/k8s/${SVC}/deployment.yaml"
done

echo "=== Applying manifests ==="

kubectl apply -f "${REPO_ROOT}/k8s/namespace.yaml"
kubectl apply -f "${REPO_ROOT}/k8s/configmap.yaml"

# Only create the secret if it doesn't already exist (avoids overwriting live values).
if ! kubectl get secret ledgerline-secrets -n ledgerline &>/dev/null; then
    echo "WARNING: ledgerline-secrets not found — applying template with placeholder values."
    echo "         Update SECRET_KEY (and DATABASE_URL if using Cloud SQL) before use."
    kubectl apply -f "${REPO_ROOT}/k8s/secret.yaml"
fi

kubectl apply -f "${REPO_ROOT}/k8s/ledger/pvc.yaml"
kubectl apply -f "${REPO_ROOT}/k8s/ledger/deployment.yaml"
kubectl apply -f "${REPO_ROOT}/k8s/ledger/service.yaml"
kubectl apply -f "${REPO_ROOT}/k8s/reminders/deployment.yaml"
kubectl apply -f "${REPO_ROOT}/k8s/reminders/service.yaml"
kubectl apply -f "${REPO_ROOT}/k8s/recommendations/deployment.yaml"
kubectl apply -f "${REPO_ROOT}/k8s/recommendations/service.yaml"
kubectl apply -f "${REPO_ROOT}/k8s/ingress.yaml"

echo "=== Restoring original manifests (removing sed substitutions) ==="

for SVC in ledger reminders recommendations; do
    mv "${REPO_ROOT}/k8s/${SVC}/deployment.yaml.bak" "${REPO_ROOT}/k8s/${SVC}/deployment.yaml"
done

echo ""
echo "=== Rollout status ==="
kubectl rollout status deployment/ledger -n ledgerline
kubectl rollout status deployment/reminders -n ledgerline
kubectl rollout status deployment/recommendations -n ledgerline

echo ""
echo "Done. Get the ingress IP with:"
echo "  kubectl get ingress ledgerline-ingress -n ledgerline"
