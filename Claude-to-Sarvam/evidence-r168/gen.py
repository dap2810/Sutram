import sys
N=int(sys.argv[2]); kind=sys.argv[1]; par=len(sys.argv)>3
body={
'A':"""mukhya() {
    vitti s = 0
    chakra i = 1 tak N {
        vitti p = nirmmita(64)
        p[0] = i
        s = s + p[0]
    }
    likha(s)
PAR}""",
'B':"""mukhya() {
    vitti s = 0
    chakra i = 1 tak N {
        mandapa {
            vitti p = nirmmita(64)
            p[0] = i
            s = s + p[0]
        }
    }
    likha(s)
PAR}""",
'C':"""mukhya() {
    vitti s = 0
    chakra i = 1 tak N {
        kosh temp[1]
        kosh_kship(temp, i)
        s = s + temp[0]
    }
    likha(s)
PAR}""",
'D':"""mukhya() {
    vitti s = 0
    chakra i = 1 tak N {
        mandapa {
            kosh temp[1]
            kosh_kship(temp, i)
            s = s + temp[0]
        }
    }
    likha(s)
PAR}""",
'G':"""mukhya() {
    kosh k[1]
    chakra i = 1 tak N {
        kosh_kship(k, i)
    }
    likha(k[N - 1])
PAR}""",
'M':"""mukhya() {
    vitti s = 0
    chakra i = 1 tak N {
        mala m[8]
        m[0] = i
        s = s + m[0]
    }
    likha(s)
PAR}""",
'Z':"""mukhya() {
    vitti s = 0
    likha(s)
PAR}""",
}[kind]
print(body.replace('N', str(N)).replace('PAR', '    likha(parimana())\n' if par else ''), end='')
