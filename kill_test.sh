#!/bin/bash
# kill_test.sh <label> <mode: poweroff|drain> <seconds> <trigger_at>
set -u
export PATH=$HOME/.local/bin:$PATH
L="$1"; MODE="$2"; SECS="${3:-420}"; TRIG="${4:-30}"
IP=$(cat lb_ip); mkdir -p out/$L
# pick a node that actually hosts pods
TARGET=$(kubectl get pods -l app=web -o jsonpath='{.items[0].spec.nodeName}')
echo "target node: $TARGET" | tee out/$L/target.txt
DROPLET=$(doctl compute droplet list --format ID,Name --no-header | awk -v n="$TARGET" '$2==n{print $1}')
echo "droplet id: $DROPLET" | tee -a out/$L/target.txt
kubectl get pods -l app=web -o wide --no-headers > out/$L/pods_before.txt 2>&1

./watch_state.sh > out/$L/state.log 2>/dev/null & W=$!
python3 load.py "http://$IP/" "$SECS" 20 out/$L/requests.json > out/$L/summary.txt 2>&1 & LOAD=$!
sleep "$TRIG"
echo "$(date +%s.%N) TRIGGER $MODE $TARGET" | tee out/$L/events.log
if [ "$MODE" = "poweroff" ]; then
  doctl compute droplet-action power-off "$DROPLET" >/dev/null 2>&1
else
  kubectl drain "$TARGET" --ignore-daemonsets --delete-emptydir-data --force --timeout=120s >out/$L/drain.txt 2>&1
fi
echo "$(date +%s.%N) ACTION_RETURNED" >> out/$L/events.log
wait $LOAD
kill $W 2>/dev/null
echo "=== $L ==="; cat out/$L/summary.txt
