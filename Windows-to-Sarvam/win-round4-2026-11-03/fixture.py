import hashlib,json,subprocess
from pathlib import Path
h=Path(__file__).resolve().parent;root=h.parents[1]
p=root/'tests/fixtures/file_hello.txt';before=p.read_bytes();cmd=['git','show','HEAD:tests/fixtures/file_hello.txt'];data=subprocess.check_output(cmd,cwd=root);p.write_bytes(data)
(h/'fixture.json').write_text(json.dumps(dict(command=cmd,before_hex=before.hex(),committed_hex=data.hex(),sha256=hashlib.sha256(data).hexdigest()),indent=2))
