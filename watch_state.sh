#!/bin/bash
# timestamped: node readiness + which pod IPs are in the Service endpoints
while true; do
  T=$(date +%s.%N)
  N=$(kubectl get nodes --no-headers 2>/dev/null | awk '{printf "%s=%s ",$1,$2}')
  E=$(kubectl get endpointslices -l kubernetes.io/service-name=web \
       -o jsonpath='{range .items[*].endpoints[*]}{.addresses[0]}={.conditions.ready}{" "}{end}' 2>/dev/null)
  printf '%s | NODES %s| EP %s\n' "$T" "$N" "$E"
  sleep 0.5
done
