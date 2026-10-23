"""Host-only structure tests. These do not invoke the Sutram compiler or network."""
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('r85_builtin_inventory',ROOT/'tools/r85_builtin_inventory.py')
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

COMPILER='''
BN_STHAGITA equ 3
BN_NETSOCK equ 9
BN_NETBIND equ 10
BN_NETLIST equ 11
BN_NETACC equ 12
bn_sthagita db "sthagita", 0
bn_netsock db "netsock", 0
bn_netbind db "netbind", 0
bn_netlist db "netlisten", 0
bn_netacc db "netaccept", 0
bn_table:
 dq bn_sthagita, TOK_BUILTIN, BN_STHAGITA
 dq bn_netsock, TOK_BUILTIN, BN_NETSOCK
 dq bn_netbind, TOK_BUILTIN, BN_NETBIND
 dq bn_netlist, TOK_BUILTIN, BN_NETLIST
 dq bn_netacc, TOK_BUILTIN, BN_NETACC
bn_table_end:
kosh_var_cnt resq 1
kosh_vars resq 256
kosh_param_var_cnt resq 1
kosh_param_vars resq 6
cmp rbx, BN_STHAGITA
je .pp_halt
call r54_builtin_arity_ok
.ge_call:
cmp r12, BN_NETSOCK
je .ge_call_netsock
cmp r12, BN_NETBIND
je .ge_call_netbind
cmp r12, BN_NETLIST
je .ge_call_netlist
cmp r12, BN_NETACC
je .ge_call_netacc
.ge_call_netbind:
mov dword [rsp+4], 0
.ge_call_netlist:
.ge_call_nirm:
.gs_halt:
mov dil, 0xF4
.gs_writemem:
.ge_halt:
mov dil, 0xF4
; emit_nirmmita_from_rax
'''
class TestInventory(unittest.TestCase):
    def test_exact_nine_classes(self):
        r=m.inspect(COMPILER)
        self.assertEqual(r['status'],'PASS')
        self.assertEqual(len(r['identifiers']),9)
        self.assertEqual(sum(row['classification']=='compiler_private_bss' for row in r['identifiers']),4)
    def test_hlt_hazard_flag(self):
        self.assertTrue(m.inspect(COMPILER)['risks']['sthagita_emits_privileged_hlt'])
    def test_wildcard_hazard_flag(self):
        self.assertTrue(m.inspect(COMPILER)['risks']['netbind_sets_ipv4_address_zero_INADDR_ANY'])
    def test_missing_builtin_dispatch_fails(self):
        bad=COMPILER.replace('je .ge_call_netacc','jne .ge_call_netacc')
        r=m.inspect(bad)
        self.assertEqual(r['status'],'FAIL')
    def test_accidental_internal_export_fails(self):
        bad=COMPILER.replace('bn_table:', 'bn_fake db \"kosh_vars\", 0\nbn_table:')
        bad=bad.replace('bn_table_end:', ' dq bn_fake, TOK_BUILTIN, BN_NETSOCK\nbn_table_end:')
        observed=m.inspect(bad)
        self.assertEqual(observed['status'],'FAIL')
        self.assertTrue(any('kosh_vars' in err for err in observed['errors']))
    def test_missing_bss_declaration_fails(self):
        bad=COMPILER.replace('kosh_vars resq 256','unrelated_vars resq 256')
        self.assertEqual(m.inspect(bad)['status'],'FAIL')
    def test_no_test_ever_calls_compiler(self):
        self.assertNotIn('subprocess',Path(m.__file__).read_text())
if __name__=='__main__':unittest.main()
