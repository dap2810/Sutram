/* ROUND-33: 3, 4 and 5 arguments; each digit says which register it came from. */
long r33_s3(long a, long b, long c) { return a * 100 + b * 10 + c; }
long r33_s4(long a, long b, long c, long d) { return a * 1000 + b * 100 + c * 10 + d; }
long r33_s5(long a, long b, long c, long d, long e) { return a * 10000 + b * 1000 + c * 100 + d * 10 + e; }
