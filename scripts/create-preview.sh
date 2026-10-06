#!/bin/bash
set -e

PR_NUMBER=$1

if [ -z "$PR_NUMBER" ]; then
  echo "Usage: ./create-preview.sh <pr-number>"
  exit 1
fi

OVERLAY_DIR="k8s/overlays/pr-$PR_NUMBER"
NAMESPACE="pr-$PR_NUMBER"

echo "Creating overlay for PR $PR_NUMBER..."

cp -r k8s/overlays/pr-template "$OVERLAY_DIR"

sed -i "s/PLACEHOLDER/$PR_NUMBER/g" "$OVERLAY_DIR/kustomization.yaml"

echo "Ensuring namespace $NAMESPACE exists..."
kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

echo "Applying to cluster..."
kubectl apply -k "$OVERLAY_DIR"

echo "Preview environment for PR $PR_NUMBER created in namespace $NAMESPACE"