// Scenario B: build a collection of 1,000,000 numbers, then sum it - an array and push
const v = [];
for (let i = 0; i < 1000000; i++) {
  v.push(i);
}
let s = 0;
for (const x of v) {
  s += x;
}
console.log(s);
