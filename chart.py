import json, pathlib, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({"figure.facecolor":"#12141a","axes.facecolor":"#12141a","axes.edgecolor":"#3a4050",
 "text.color":"#e6e8ee","axes.labelcolor":"#e6e8ee","xtick.color":"#9aa3b5","ytick.color":"#9aa3b5",
 "font.size":11,"grid.color":"#232733"})
G=[("Cluster","default: externalTrafficPolicy: Cluster",
    ["T1_cluster_poweroff","T_Cluster_r2","T_Cluster_r3","T_Cluster_r4","T_Cluster_r5"],"#e5484d"),
   ("Local","externalTrafficPolicy: Local",
    ["T2_local_poweroff","T_Local_r2","T_Local_r3","T_Local_r4","T_Local_r5"],"#4a9eff")]
fig=plt.figure(figsize=(12.5,8.8)); gs=fig.add_gridspec(2,1,height_ratios=[1.45,1],hspace=0.40)
ax=fig.add_subplot(gs[0]); row=0; ticks=[]; labels=[]
for key,title,names,col in G:
    for i,n in enumerate(names):
        d=pathlib.Path("out")/n
        reqs=json.load(open(d/"requests.json")); trig=float(open(d/"events.log").read().split()[0])
        f=[x[0]-trig for x in reqs if x[2]!=200]
        ax.scatter(f,[row]*len(f),s=56,marker="x",lw=2,color=col)
        ticks.append(row); labels.append(f"{key}  run {i+1}")
        row+=1
    row+=0.6
ax.axvline(0,color="#f5a524",ls="--",lw=1.6)
ax.text(2.0,row-1.2,"node powered off",color="#f5a524",fontsize=10)
ax.axvspan(0,13.2,color="#f5a524",alpha=.08,lw=0)
ax.set_yticks(ticks); ax.set_yticklabels(labels,fontsize=9.5); ax.invert_yaxis()
ax.set_xlim(-12,152); ax.set_xlabel("seconds relative to the node being powered off")
ax.grid(axis="x",alpha=.3,lw=.6)
ax.set_title("Every failed request, ten runs. Same totals, different distribution.",loc="left",pad=10,fontsize=12.5)
ax2=fig.add_subplot(gs[1])
ev=[("node marked NotReady",2.9,"#4a9eff"),("endpoints updated",13.2,"#e5484d"),
    ("endpoints updated\nafter a clean drain",0.5,"#3fb950")]
for i,(lab,v,c) in enumerate(ev):
    ax2.barh(i,v,color=c,edgecolor="#12141a",lw=1.5,height=.62)
    ax2.text(v+0.35,i,f"{v}s",va="center",color="#e6e8ee",fontsize=11)
ax2.axvline(40,color="#9aa3b5",ls=":",lw=1.4)
ax2.text(41.0,0.15,"40s, the documented\nnode-monitor-grace-period\ndefault",color="#9aa3b5",fontsize=9.5,va="center")
ax2.set_yticks(range(len(ev))); ax2.set_yticklabels([e[0] for e in ev],fontsize=10); ax2.invert_yaxis()
ax2.set_xlim(0,62); ax2.set_xlabel("seconds after the node died (median of 10 runs)")
ax2.grid(axis="x",alpha=.3,lw=.6)
ax2.set_title("Detection is fast. Taking the pods out of rotation is not.",loc="left",pad=10,fontsize=12.5)
fig.suptitle("I pulled the power on a Kubernetes node, ten times",x=0.06,ha="left",fontsize=14.5,y=0.985)
fig.text(0.06,0.948,"DOKS 1.36.3, 3 nodes, 6 replicas behind a cloud load balancer, ~175 req/s with keep-alive clients.",
         ha="left",fontsize=10,color="#9aa3b5")
fig.subplots_adjust(left=0.175,right=0.97,top=0.90,bottom=0.07)
fig.savefig("results.png",dpi=145); print("wrote results.png")
