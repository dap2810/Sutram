import sys
shape=sys.argv[1]
body={'direct':'        kosh temp[1]\n        kosh_kship(temp, j)\n        s = s + temp[0]\n',
      'mandapa':'        mandapa {\n            kosh temp[1]\n            kosh_kship(temp, j)\n            s = s + temp[0]\n        }\n',
      'yadi':'        yadi (j > 0) {\n            kosh temp[1]\n            kosh_kship(temp, j)\n            s = s + temp[0]\n        }\n'}[shape]
print('prakriya ruk(n) {\n    likha(n)\n    vitti x = grahan()\n    nivartanam x\n}\nmukhya() {\n    vitti s = 0\n    vitti t = ruk(0)\n    chakra j = 1 tak 800000 {\n'+body+'        yadi (j == 400000) {\n            t = ruk(j)\n        }\n    }\n    t = ruk(800000)\n    likha(s)\n}')
