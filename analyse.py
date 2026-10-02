import json, pathlib, statistics, re

def load(d):
    reqs=json.load(open(d/"requests.json"))
    trig=float(open(d/"events.log").read().split()[0])
    f=sorted([r for r in reqs if r[2]!=200], key=lambda r:r[0])
    near=[x for x in f if x[0]-trig <= 60]      # attributable to the node loss
    late=[x for x in f if x[0]-trig > 60]       # separate, unexplained
    win = (near[-1][0]-near[0][0]) if len(near)>1 else 0.0
    first = (near[0][0]-trig) if near else None
    notready=epupd=None
    pn=pe=None
    for line in open(d/"state.log"):
        if "|" not in line: continue
        t=float(line.split("|")[0])-trig
        n=line.split("NODES")[1].split("| EP")[0].strip(); e=line.split("| EP")[1].strip()
        if pn is not None and n!=pn and notready is None and t>0 and ("NotReady" in n or "SchedulingDisabled" in n):
            notready=t
        if pe is not None and e!=pe and epupd is None and t>0: epupd=t
        pn,pe=n,e
    return dict(runs=len(reqs), near=len(near), late=len(late), first=first, window=win,
                notready=notready, epupd=epupd)

GROUPS={"Cluster (default)":["T1_cluster_poweroff","T_Cluster_r2","T_Cluster_r3","T_Cluster_r4","T_Cluster_r5"],
        "Local":["T2_local_poweroff","T_Local_r2","T_Local_r3","T_Local_r4","T_Local_r5"],
        "clean drain (control)":["T3_clean_drain"]}
out={}
print(f"{'run':<22}{'reqs':>8}{'fails':>7}{'late':>6}{'first':>8}{'window':>9}{'NotReady':>10}{'endpoints':>11}")
for g,names in GROUPS.items():
    rows=[]
    for n in names:
        d=pathlib.Path("out")/n
        if not (d/"requests.json").exists(): continue
        r=load(d); rows.append(r)
        print(f"{n:<22}{r['runs']:>8}{r['near']:>7}{r['late']:>6}"
              f"{(f'{r['first']:+.1f}s' if r['first'] is not None else '-'):>8}"
              f"{r['window']:>8.1f}s{(f'{r['notready']:.1f}s' if r['notready'] else '-'):>10}"
              f"{(f'{r['epupd']:.1f}s' if r['epupd'] else '-'):>11}")
    out[g]=rows
print()
for g,rows in out.items():
    if not rows: continue
    fa=[r['near'] for r in rows]; wi=[r['window'] for r in rows]
    nr=[r['notready'] for r in rows if r['notready']]; ep=[r['epupd'] for r in rows if r['epupd']]
    print(f"{g}:  n={len(rows)}")
    print(f"   failures  median {statistics.median(fa):.0f}   range {min(fa)}-{max(fa)}")
    print(f"   window    median {statistics.median(wi):.1f}s range {min(wi):.1f}-{max(wi):.1f}s")
    if nr: print(f"   NotReady  median {statistics.median(nr):.1f}s range {min(nr):.1f}-{max(nr):.1f}s")
    if ep: print(f"   endpoints median {statistics.median(ep):.1f}s range {min(ep):.1f}-{max(ep):.1f}s")
json.dump({g:[r for r in rows] for g,rows in out.items()}, open("analysis.json","w"), indent=1)
