from pathlib import Path
import os,sys,subprocess,time,json,platform
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
env=dict(os.environ,SUTRAM_EVIDENCE=str(HERE))
cmd=[sys.executable,str(ROOT/'tools/test_windows_native.py')]
started=time.time();t=time.perf_counter();p=subprocess.run(cmd,cwd=ROOT,env=env,capture_output=True,timeout=600)
elapsed=time.perf_counter()-t
(HERE/'suite-stdout.txt').write_bytes(p.stdout);(HERE/'suite-stderr.txt').write_bytes(p.stderr)
r=dict(command=cmd,cwd=str(ROOT),started_epoch=started,elapsed_seconds=elapsed,exit=p.returncode,stdout=p.stdout.decode('utf8','replace'),stderr=p.stderr.decode('utf8','replace'),python=sys.version,platform=platform.platform(),comparison_reference_seconds=18.6,ratio_to_reference=elapsed/18.6,measurement_scope='One wall-clock run of the existing native suite. Run after reinstall and identity verification, without concurrent installer work; one sample, not a controlled compiler microbenchmark.')
(HERE/'suite-timing.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf8');print(json.dumps(r,indent=2));raise SystemExit(p.returncode)
