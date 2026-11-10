// Scenarios C and D: fill a buffer of n numbers, then sum all of it r times (arguments: r n)
fn main() {
    let r: usize = std::env::args().nth(1).and_then(|a| a.parse().ok()).unwrap_or(1);
    let n: usize = std::env::args().nth(2).and_then(|a| a.parse().ok()).unwrap_or(10_000_000);
    let mut p: Vec<i64> = (0..n).map(|i| (i & 1023) as i64).collect();
    let mut t: i64 = 0;
    for q in 0..r {
        p[q] += 1;
        t += p.iter().sum::<i64>();
    }
    println!("{}", t);
}
