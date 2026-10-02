#!/bin/bash
set -u; cd ~/k8snode; export PATH=$HOME/.local/bin:$PATH
restore(){
  D=$(grep "droplet id" "out/$1/target.txt" | awk '{print $3}')
  doctl compute droplet-action power-on "$D" --wait >/dev/null 2>&1
  for i in $(seq 1 40); do [ "$(kubectl get nodes --no-headers 2>/dev/null | grep -c ' Ready ')" -ge 3 ] && break; sleep 15; done
  kubectl delete pods -l app=web --wait=false >/dev/null 2>&1; sleep 10
  kubectl rollout status deploy/web --timeout=300s >/dev/null 2>&1; sleep 20
  IP=$(cat lb_ip); for i in $(seq 1 30); do [ "$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 http://$IP/ 2>/dev/null)" = "200" ] && break; sleep 5; done
}
for rep in 4 5; do
  for pol in Cluster Local; do
    kubectl patch svc web -p "{\"spec\":{\"externalTrafficPolicy\":\"$pol\"}}" >/dev/null 2>&1
    sleep 40
    IP=$(cat lb_ip); for i in $(seq 1 30); do [ "$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 http://$IP/ 2>/dev/null)" = "200" ] && break; sleep 5; done
    L="T_${pol}_r${rep}"
    echo "--- $L ---"
    ./kill_test.sh "$L" poweroff 150 30 2>&1 | tail -3
    restore "$L"
  done
done
echo "ALL REPEATS DONE"
