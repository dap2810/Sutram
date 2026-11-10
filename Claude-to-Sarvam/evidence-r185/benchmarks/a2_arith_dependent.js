// Scenario A2: 10,000,000 passes of s = (s + i * 2) ^ (s >> 3), on 64-bit integers (BigInt: a
// JavaScript number cannot hold them, and its ^ works on 32 bits)
let s = 0n;
for (let i = 0n; i < 10000000n; i++) {
  s = BigInt.asIntN(64, (s + i * 2n) ^ (s >> 3n));
}
console.log(s.toString());
