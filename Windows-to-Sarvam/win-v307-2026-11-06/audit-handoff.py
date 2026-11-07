"""Validate the claims and local links in the completed evidence package."""
from pathlib import Path
import ast,json,re,subprocess,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
read=lambda n:json.loads((HERE/n).read_text(encoding='utf-8-sig'))
oom=read('oom.json')
assert len(oom['runs'])==32
assert sum(x['clean_refusal'] for x in oom['runs'])==14
assert sum(x['exit']==0xc00000fd for x in oom['runs'])==18
for row in oom['runs']:
    assert (HERE/row['stderr_file']).read_bytes().hex()==row['stderr_hex']
    assert row['stderr_exact'] and row['stderr_ends_lf'] and not row['timed_out']
    if '--staged' in sys.argv:
        path=(HERE/row['stderr_file']).relative_to(ROOT).as_posix()
        assert subprocess.check_output(['git','show',':'+path],cwd=ROOT).hex()==row['stderr_hex']
if '--staged' in sys.argv:
    names=subprocess.check_output(['git','diff','--cached','--name-only'],cwd=ROOT,text=True).splitlines()
    allowed={'ChatGPT-to-Sarvam/WINDOWS-V307-2026-11-06.md','ChatGPT-to-Sarvam/WINDOWS-HANDOFF-INDEX-2026-11-06.md'}
    assert all(n in allowed or n.startswith('Windows-to-Sarvam/win-v307-2026-11-06/') for n in names)
    for relative in ('interrupted-payload.pending.sha256','reader-interference/interrupted-payload.pending.sha256'):
        path=HERE/relative
        assert subprocess.check_output(['git','show',':'+path.relative_to(ROOT).as_posix()],cwd=ROOT)==path.read_bytes()
assert read('suite.json')['counts']['PASS']==322 and not read('suite.json')['failures']
identity=read('identity.json')
assert identity['identity_pass'] and identity['manifest']==dict(total=657,passed=657,failures=[])
assert read('final-state.json')['pass']
upgrade=read('upgrade.json')
assert upgrade['status']=='NO_RESULT_AFTER_935_SECONDS' and upgrade['observed_seconds']>=935
assert read('restore-upgrade.json')['pass']
assert read('interrupt.json')['status']=='INTERRUPTED_AS_REQUESTED'
recovery=read('recovery.json')
assert recovery['status']=='FINISH' and recovery['child_exit']==0 and recovery['closed_after_finish_click'] and not recovery['pending_exists']
assert read('log-reader-check.json')['add_content_with_reader']=='FAIL'
assert read('log-reader-check.json')['add_content_after_reader_closed']=='PASS'
for file in HERE.glob('*.py'):ast.parse(file.read_text(encoding='utf8'),filename=str(file))
docs=[HERE/n for n in ('OOM.md','UPGRADE.md','SLICE.md','COMMANDS.md')]
docs += [ROOT/'ChatGPT-to-Sarvam'/n for n in ('WINDOWS-V307-2026-11-06.md','WINDOWS-HANDOFF-INDEX-2026-11-06.md')]
links=0
for doc in docs:
    text=doc.read_text(encoding='utf8')
    assert 'local draft' not in text and 'pending the active' not in text
    for target in re.findall(r'\]\(([^)\n]+)\)',text):
        if re.match(r'\w+://',target):continue
        target=target.split('#')[0]
        if target: assert (doc.parent/target).exists(),(doc,target)
        links+=1
r=dict(pass_=True,local_links_checked=links,oom_runs=32,abnormal_oom_exits=18,suite_pass=322,manifest_pass=657,recovery_seconds=recovery['finish_seconds'],upgrade_observed_seconds=upgrade['observed_seconds'])
if '--staged' not in sys.argv:(HERE/'audit-handoff.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf8')
print(json.dumps(r,indent=2))
