// Scenario A: 10,000,000 passes of s = s + i * 2
let s = 0;
for (let i = 0; i < 10000000; i++) {
  s = s + i * 2;
}
console.log(s);
