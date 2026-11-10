// Scenarios C and D: fill a buffer of n numbers, then sum all of it r times (arguments: r n) - a Float64Array
// (a JavaScript number is a double; these sums stay below 2^53, so they are exact)
const r = process.argv.length > 2 ? parseInt(process.argv[2], 10) : 1;
const n = process.argv.length > 3 ? parseInt(process.argv[3], 10) : 10000000;
const p = new Float64Array(n);
for (let i = 0; i < p.length; i++) {
  p[i] = i & 1023;
}
let t = 0;
for (let q = 0; q < r; q++) {
  p[q] += 1;
  let s = 0;
  for (let j = 0; j < p.length; j++) {
    s += p[j];
  }
  t += s;
}
console.log(t);
