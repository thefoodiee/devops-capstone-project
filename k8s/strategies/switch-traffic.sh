#!/usr/bin/env bash
# Script to switch live traffic between Blue and Green deployments in Kubernetes
set -e

TARGET_SLOT="${1:-green}"

if [ "$TARGET_SLOT" != "blue" ] && [ "$TARGET_SLOT" != "green" ]; then
    echo "Usage: $0 [blue|green]"
    exit 1
fi

echo "==> Switching live service selector to slot: ${TARGET_SLOT}"
kubectl patch service notes-live-service -n notes-app -p "{\"spec\":{\"selector\":{\"slot\":\"${TARGET_SLOT}\"}}}"

echo "==> Verifying traffic routing..."
kubectl get service notes-live-service -n notes-app -o jsonpath='{.spec.selector}'
echo ""
echo "Traffic successfully switched to ${TARGET_SLOT}!"
