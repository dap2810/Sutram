"""Record the promotion of the verified experiment and harness corrections."""
from pathlib import Path
root=Path(__file__).resolve().parents[2]
p=root/'src/r65_arena.inc'
s=p.read_text();s=s.replace('%ifndef WR4_EXPERIMENT\n    cmp qword [rel target_pe], 0\n    jne .no\n%endif\n','')
s=s.replace('; r65_active -> rax = 1 when the arena path applies to this build: a Linux ELF target.', '; r65_active -> shared ELF/PE arena; GUARD_PAGES retains independent allocations.\n; PE uses VirtualAlloc RESERVE|COMMIT: 1 GiB commit charge, not lazy Linux mmap.')
p.write_text(s)
p=root/'src/sutram_compiler.asm';s=p.read_text()
s=s.replace('%ifndef WR4_EXPERIMENT\n    cmp qword [rel target_pe], 0\n    jne .wr3_unsupported\n%endif\n','')
start=s.index('.wr3_unsupported:\n');end=s.index('.bad:',start);s=s[:start]+s[end:]
start=s.index('%ifndef WR4_EXPERIMENT\n    cmp rbx, BN_PARIMANA');end=s.index('%endif\n',start)+len('%endif\n');s=s[:start]+s[end:]
s='\n'.join(line for line in s.split('\n') if not any(x in line for x in ('wr3_memory_hdr db','wr3_query_txt db','wr3_budget_txt db','wr3_memory_hint db')))
s=s.replace('Now, on Linux ELF, a kosh is','Now, on ELF and PE, a kosh is')
s=s.replace(';; made in its own mmap reservation of R101A_REGION bytes, MAP_NORESERVE: pages are committed',';; made in its own region of R101A_REGION bytes. On Linux MAP_NORESERVE pages are committed')
s=s.replace(';; path), not in the GUARD_PAGES build, not on PE (r65_active is 0 there): unchanged.',';; path), not in the GUARD_PAGES build. PE commits the whole region via VirtualAlloc.')
s=s.replace('(Linux ELF, not --fail-alloc)','(ELF/PE, not --fail-alloc)')
p.write_text(s)
p=root/'tools/test_windows_native.py';s=p.read_text().replace("    if re.search(r'", "    if source.stem == '29_nishkriya':\n        skipped.append({'case':source.stem,'status':'SKIP_LINUX_RAW_SYSCALL','reason':'yantra emits raw Linux exit syscall 60; not a Windows ABI program'})\n        continue\n    if re.search(r'",1)
s=s.replace("langs={'37_native_gujarati'", "langs={'220_hindi_parse_error':'hindi','37_native_gujarati'")
p.write_text(s)
p=root/'tests/windows_round3/test_contract.py';s=p.read_text();start=s.index('    def test_pe_memory_features_refuse');end=s.index('    @unittest.skipIf',start)
s=s[:start]+'''    def test_pe_memory_features_compile(self):
        for name, source in [('query', 'mukhya() { likha(parimana()) }'), ('budget', 'mukhya() { mandapa parimita 64 { likha(1) } }')]:
            result, target = self.compile(source, name, pe=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(target.exists())

'''+s[end:]
s=s.replace("    @unittest.skipIf(os.name == 'nt', 'Linux region accounting has no Windows implementation')\n",'')
s=s.replace('def test_elf_accounting_and_budget_still_work', 'def test_accounting_and_budget_work')
p.write_text(s)
