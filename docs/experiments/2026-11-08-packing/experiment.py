"""Synthetic packing experiment. Run with Python + ortools==9.15.6755.
Outputs results.json and comparison.svg beside this script. No PDK units.
"""
import json, time, copy
from pathlib import Path
from itertools import combinations
import ortools
from ortools.sat.python import cp_model
OUT=Path(__file__).resolve().parent
DIMS=[('A',8,6),('B',8,6),('C',6,9),('D',5,7),('E',7,4),('F',4,5),('G',3,8),('H',6,3)]
BOXES={n:[(0,0,w,h)] for n,w,h in DIMS}
CASES=[dict(name='rectangles',shapes=BOXES,gap=1,special=False),dict(name='relations',shapes=BOXES,gap=1,special=True),dict(name='stepped',shapes={'L':[(0,0,4,10),(4,0,6,4)],'Q':[(0,0,6,6)]},gap=0,special=False)]
def bounds(parts): return max(a+w for a,b,w,h in parts),max(b+h for a,b,w,h in parts)
def gap(c,a,b): return 3 if c['special'] and set((a,b))=={'C','D'} else c['gap']
def check(c,r):
    errs=[]; p=r['positions']; W,H=r['bbox']
    if set(p)!=set(c['shapes']): return ['object_set']
    for a,parts in c['shapes'].items():
        x,y=p[a]
        if not isinstance(x,int) or not isinstance(y,int): errs.append('grid:'+a)
        for dx,dy,w,h in parts:
            if min(x+dx,y+dy)<0 or x+dx+w>W or y+dy+h>H: errs.append('boundary:'+a)
    for a,b in combinations(c['shapes'],2):
        g=gap(c,a,b)
        for ax,ay,aw,ah in c['shapes'][a]:
            for bx,by,bw,bh in c['shapes'][b]:
                a_x=ax+p[a][0]; a_y=ay+p[a][1]; b_x=bx+p[b][0]; b_y=by+p[b][1]
                if not (a_x+aw+g<=b_x or b_x+bw+g<=a_x or a_y+ah+g<=b_y or b_y+bh+g<=a_y): errs.append('separation:'+a+':'+b)
    if c['special']:
        if p['A'][1]!=p['B'][1]: errs.append('align:A:B')
        if p['A'][0]+8+1>p['B'][0]: errs.append('left:A:B')
    if r['area']!=W*H: errs.append('area')
    return errs

def shelf(c):
    start=time.perf_counter(); dims={n:bounds(v) for n,v in c['shapes'].items()}; candidates=[]; count=0
    orders=[list(dims),sorted(dims,key=lambda n:(-dims[n][1],-dims[n][0]))]
    for order in orders:
        for target in range(max(w for w,h in dims.values()),sum(w for w,h in dims.values())+len(dims)*3+1):
            rows=[]
            for n in order:
                w,h=dims[n]; placed=False
                for row in rows:
                    if row['w']+c['gap']+w<=target and h<=row['h']:
                        row['items'].append((n,row['w']+c['gap'])); row['w']+=c['gap']+w; placed=True;break
                if not placed: rows.append(dict(items=[(n,0)],w=w,h=h))
            p={}; y=0
            for row in rows:
                for n,x in row['items']: p[n]=[x,y]
                y+=row['h']+c['gap']
            W=max(row['w'] for row in rows); H=y-c['gap']; r=dict(positions=p,bbox=[W,H],area=W*H)
            count+=1
            if not check(c,r): candidates.append(r)
    if not candidates: raise RuntimeError('No valid shelf baseline')
    r=min(candidates,key=lambda r:(r['area'],sum(r['bbox'])))
    return dict(r,status='HEURISTIC',seconds=time.perf_counter()-start,candidates=count,validated=True)

def solve(c,seconds,baseline=None,limit=100):
    m=cp_model.CpModel(); xs={};ys={};ix=[];iy=[]
    W=m.new_int_var(1,limit,'W');H=m.new_int_var(1,limit,'H');A=m.new_int_var(1,limit*limit,'area')
    m.add_multiplication_equality(A,[W,H]);m.minimize(A)
    m.add(A >= sum(w*h for parts in c['shapes'].values() for dx,dy,w,h in parts))
    for n,parts in c['shapes'].items():
        xs[n]=m.new_int_var(0,limit,n+'x');ys[n]=m.new_int_var(0,limit,n+'y')
        for k,(dx,dy,w,h) in enumerate(parts):
            m.add(xs[n]+dx+w<=W);m.add(ys[n]+dy+h<=H)
            ix.append(m.new_fixed_size_interval_var(xs[n]+dx,w,n+str(k)+'ix'))
            iy.append(m.new_fixed_size_interval_var(ys[n]+dy,h,n+str(k)+'iy'))
    m.add_no_overlap_2d(ix,iy)
    for a,b in combinations(c['shapes'],2):
        g=gap(c,a,b)
        if not g: continue
        for k,(ax,ay,aw,ah) in enumerate(c['shapes'][a]):
            for j,(bx,by,bw,bh) in enumerate(c['shapes'][b]):
                bs=[m.new_bool_var(f'{a}{b}{k}{j}{t}') for t in range(4)]
                for expr,lit in zip([xs[a]+ax+aw+g<=xs[b]+bx,xs[b]+bx+bw+g<=xs[a]+ax,ys[a]+ay+ah+g<=ys[b]+by,ys[b]+by+bh+g<=ys[a]+ay],bs):m.add(expr).only_enforce_if(lit)
                m.add_bool_or(bs)
    if c['special']:
        m.add(ys['A']==ys['B']);m.add(xs['A']+9<=xs['B'])
    if baseline:
        m.add(A<=baseline['area'])
        for n,(x,y) in baseline['positions'].items(): m.add_hint(xs[n],x);m.add_hint(ys[n],y)
        m.add_hint(W,baseline['bbox'][0]);m.add_hint(H,baseline['bbox'][1]);m.add_hint(A,baseline['area'])
    s=cp_model.CpSolver();s.parameters.max_time_in_seconds=seconds;s.parameters.num_search_workers=1;s.parameters.random_seed=0
    start=time.perf_counter();status=s.solve(m);elapsed=time.perf_counter()-start
    r=dict(status=s.status_name(status),seconds=elapsed,budget_seconds=seconds,best_bound=s.best_objective_bound)
    if status in (cp_model.OPTIMAL,cp_model.FEASIBLE):
        r.update(positions={n:[s.value(xs[n]),s.value(ys[n])] for n in xs},bbox=[s.value(W),s.value(H)],area=s.value(A))
        errors=check(c,r);assert not errors,errors;r['validated']=True
    return r

def main():
    results=[]
    for c in CASES:
        base=shelf(c); runs=[solve(c,t,base) for t in (1,5)]
        best=min([base]+[r for r in runs if 'area' in r],key=lambda r:r['area'])
        bad=copy.deepcopy(best); names=list(c['shapes']);bad['positions'][names[1]]=bad['positions'][names[0]][:]
        failures=check(c,bad);assert failures
        impossible=solve(c,1,limit=2);assert impossible['status']=='INFEASIBLE'
        record=dict(case=c,baseline=base,runs=runs,tamper_detected=failures,infeasible=impossible)
        results.append(record); print(c['name'],base['area'],[(r['status'],r.get('area'),r['best_bound']) for r in runs],flush=True)
    (OUT/'results.json').write_text(json.dumps(dict(ortools=ortools.__version__,grid='synthetic integer units',seed=0,workers=1,results=results),indent=2))
    colors=['#60a5fa','#34d399','#fbbf24','#fb7185','#a78bfa','#22d3ee','#f97316','#94a3b8']
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1060" viewBox="0 0 1200 1060">','<rect width="1200" height="1060" fill="#f8fafc"/>','<g font-family="sans-serif" fill="#0f172a">','<text x="30" y="35" font-size="24">Constraint packing experiment | synthetic units | no rotation</text>']
    for row,rec in enumerate(results):
        c=rec['case']; base=rec['baseline'];best=min([r for r in rec['runs'] if 'area' in r],key=lambda r:(r['area'],r['status']!='OPTIMAL'));scale=min(500/max(base['bbox'][0],best['bbox'][0]),225/max(base['bbox'][1],best['bbox'][1]))
        for col,(label,r) in enumerate([('Shelf width sweep',base),('CP-SAT',best)]):
            ox=30+col*590;oy=115+row*320;w,h=r['bbox']
            svg.append(f'<text x="{ox}" y="{oy-38}" font-size="18">{c["name"]} | {label} | {r["status"]}</text>')
            svg.append(f'<text x="{ox}" y="{oy-15}" font-size="15">{w} x {h} = {r["area"]} | {r["seconds"]:.3f}s | checked</text>')
            svg.append(f'<rect x="{ox}" y="{oy}" width="{w*scale}" height="{h*scale}" fill="white" stroke="#0f172a" stroke-width="2"/>')
            for i,(n,parts) in enumerate(c['shapes'].items()):
                x,y=r['positions'][n]
                for dx,dy,rw,rh in parts:svg.append(f'<rect x="{ox+(x+dx)*scale}" y="{oy+(y+dy)*scale}" width="{rw*scale}" height="{rh*scale}" fill="{colors[i]}" stroke="white"/>')
                dx,dy,rw,rh=parts[0];svg.append(f'<text x="{ox+(x+dx+rw/2)*scale}" y="{oy+(y+dy+rh/2)*scale+5}" text-anchor="middle" font-size="16">{n}</text>')
    svg.append('<text x="30" y="1040" font-size="14">Relations: A left of B, same Y; C-D gap 3; other gaps 1. Stepped: gap 0, cavity use allowed.</text></g></svg>')
    (OUT/'comparison.svg').write_text('\n'.join(svg))
if __name__=='__main__':main()
