#!/bin/bash
set -e

PR_NUMBER=$1

if [ -z "$PR_NUMBER" ]; then
  echo "Usage: ./destroy-preview.sh <pr-number>"
  exit 1
fi

NAMESPACE="pr-$PR_NUMBER"
OVERLAY_DIR="k8s/overlays/pr-$PR_NUMBER"

echo "Deleting namespace $NAMESPACE..."
kubectl delete namespace "$NAMESPACE" --ignore-not-found=true

echo "Removing local overlay folder..."
rm -rf "$OVERLAY_DIR"

echo "Preview environment for PR $PR_NUMBER destroyed"