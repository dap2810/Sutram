/* ROUND-33: the same symbols, the digits the other way round (a changed foreign object). */
long r33_s3(long a, long b, long c) { return c * 100 + b * 10 + a; }
long r33_s4(long a, long b, long c, long d) { return d * 1000 + c * 100 + b * 10 + a; }
long r33_s5(long a, long b, long c, long d, long e) { return e * 10000 + d * 1000 + c * 100 + b * 10 + a; }
