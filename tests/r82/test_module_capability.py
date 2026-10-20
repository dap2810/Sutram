import importlib.util
from pathlib import Path
import unittest
spec=importlib.util.spec_from_file_location('cap',Path(__file__).resolve().parents[2]/'tools/r82_module_capability.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class Capability(unittest.TestCase):
    def sample(self, etype='2'):
        return ('''do_main:\n    call write_elf\nwrite_elf:\n    cmp qword [rel target_pe],0\n    jne write_pe\n'''
                f'    mov word [rsp+16], {etype}\n    ret\nwant_pe:\n    ret\nwrite_pe:\n    ret\n')
    def test_real_writer_type2_detected(self):
        r=m.inspect(self.sample())
        self.assertEqual(r['status'],'STATIC_ET_EXEC_ONLY_OBSERVED')
        self.assertEqual(r['native_compile_link_test'],'NOT_RUN')
    def test_object_type1_does_not_satisfy_type2_test(self):
        self.assertEqual(m.inspect(self.sample('1'))['status'],'STATIC_INCONCLUSIVE')
    def test_duplicate_header_assignment_inconclusive(self):
        src=self.sample().replace('    mov word [rsp+16], 2','    mov word [rsp+16], 2\n    mov word [rsp+16], 2')
        self.assertEqual(m.inspect(src)['status'],'STATIC_INCONCLUSIVE')
    def test_duplicated_writer_decl_inconclusive(self):
        self.assertEqual(m.inspect(self.sample()+'write_elf:\n')['status'],'STATIC_INCONCLUSIVE')
    def test_missing_main_dispatch_inconclusive(self):
        self.assertEqual(m.inspect(self.sample().replace('call write_elf','call something_else'))['status'],'STATIC_INCONCLUSIVE')
    def test_not_mistake_comments_for_e_type(self):
        src=self.sample('1').replace('    mov word [rsp+16], 1','    mov word [rsp+16], 1\n ; mov word [rsp+16], 2')
        self.assertEqual(m.inspect(src)['status'],'STATIC_INCONCLUSIVE')

if __name__=='__main__':unittest.main()
