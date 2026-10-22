# Every library function that allocates, called once after its setup; prints its result.
SETS = '''    vitti a = rakh_srij(4)
    vitti b = rakh_srij(4)
    vitti o = rakh_srij(8)
    rakh_yuj(a, 4, "x", 1)
    rakh_yuj(a, 4, "y", 1)
    rakh_yuj(b, 4, "y", 1)
'''
PROBES = {
 'rakh_samroop_diff': ('sangrah', SETS, 'rakh_samroop_diff(a, 4, b, 4, o)', 3),
 'rakh_sangam':       ('sangrah', SETS, 'rakh_sangam(a, 4, b, 4, o)', 3),
 'rakh_sampat':       ('sangrah', SETS, 'rakh_sampat(a, 4, b, 4, o)', 3),
 'rakh_bhed':         ('sangrah', SETS, 'rakh_bhed(a, 4, b, 4, o)', 3),
 'rakh_asti_upasamuh':('sangrah', SETS, 'rakh_asti_upasamuh(b, 4, a, 4)', 3),
 'rakh_sam':          ('sangrah', SETS, 'rakh_sam(b, 4, b, 4)', 3),
 'rakh_tak_mala':     ('sangrah', SETS + '    vitti t = nirmmita(64 * 8)\n', 'rakh_tak_mala(a, 4, t)', 4),
 'nighantu_mil':      ('nighantu', '''    vitti a = nighantu_srij(4)
    vitti b = nighantu_srij(4)
    nighantu_khip(a, 4, "k", 1, 5)
''', 'nighantu_mil(b, 4, a, 4)', 2),
 'brihat_shesh':      ('brihat', '''    vitti x = nirmmita(16 * 8)
    vitti m = nirmmita(8 * 8)
    vitti r = nirmmita(8 * 8)
    brihat_ank_se_int(12345, x, 16)
    brihat_ank_se_int(97, m, 8)
''', 'brihat_shesh(x, m, r, 8)', 3),
 'brihat_ghatmod':    ('brihat', '''    vitti x = nirmmita(8 * 8)
    vitti m = nirmmita(8 * 8)
    vitti r = nirmmita(8 * 8)
    brihat_ank_se_int(3, x, 8)
    brihat_ank_se_int(97, m, 8)
''', 'brihat_ghatmod(x, 5, m, r, 8)', 3),
 'brihat_ank_tak':    ('aadhar', '''    vitti x = nirmmita(4 * 8)
    vitti o = nirmmita(16 * 8)
    brihat_ank_se_int(13, x, 4)
''', 'brihat_ank_tak(x, 4, 2, o)', 2),
 'mil_shreni':        ('shreni', '''    vitti a = nirmmita(4 * 8)
    a[0] = 3
    a[1] = 1
    a[2] = 2
    a[3] = 0
''', 'mil_shreni(a, 4)', 1),
 'roop_ank':          ('roop', '    vitti o = nirmmita(32)\n', 'roop_ank(42, o)', 1),
 'roop_ank_aadhar':   ('roop', '    vitti o = nirmmita(80)\n', 'roop_ank_aadhar(42, 2, 0, o)', 1),
 'roop_varg_ank':     ('roop', '    vitti o = nirmmita(40)\n', 'roop_varg_ank(1234567, 1, o)', 1),
 'roop_sthir_mool':   ('roop', '    vitti o = nirmmita(40)\n', 'roop_sthir(3.25, 2, o)', 1),
 'roop_chinhit':      ('roop', '    vitti o = nirmmita(40)\n', 'roop_chinhit(42, o)', 1),
 'roop_sign_akshar':  ('roop', '    vitti o = nirmmita(40)\n', 'roop_sign_akshar(42, 32, o)', 1),
 'ank_tak_varna':     ('vakyank', '    vitti o = nirmmita(24 * 8)\n', 'ank_tak_varna(42, o)', 1),
 'ank_tak_aadhar_varna': ('vakyank', '    vitti o = nirmmita(72 * 8)\n', 'ank_tak_aadhar_varna(42, 2, o)', 1),
}

def program(name):
    mod, setup, call, _ = PROBES[name]
    return f'yoj {mod}\nmukhya() {{\n{setup}    likha({call})\n    likha("\\n")\n}}\n'
# controls: functions that already checked their allocation (R9/R35/R36)
PROBES.update({
 'suchi_srij':   ('suchi', '', 'suchi_srij(4)', 0),
 'suchi_khip':   ('suchi', '    vitti l = suchi_srij(1)\n    suchi_khip(l, 1)\n', 'suchi_khip(l, 2)', 2),
 'avali_srij':   ('suchi', '', 'avali_srij(4)', 0),
 'avali_pravesh':('suchi', '    vitti q = avali_srij(1)\n    avali_pravesh(q, 1)\n', 'avali_pravesh(q, 2)', 2),
 'nighantu_srij':('nighantu', '', 'nighantu_srij(4)', 0),
 'nighantu_vardh':('nighantu', '    vitti m = nighantu_srij(2)\n    nighantu_khip(m, 2, "k", 1, 5)\n', 'nighantu_vardh(m, 8) != 0', 1),
 'mala_nava':    ('mala', '', 'mala_nava(4) != 0', 0),
})
