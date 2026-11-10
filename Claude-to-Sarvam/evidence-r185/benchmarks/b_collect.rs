// Scenario B: build a collection of 1,000,000 numbers, then sum it - Vec
fn main() {
    let mut v: Vec<i64> = Vec::new();
    for i in 0..1_000_000i64 {
        v.push(i);
    }
    let s: i64 = v.iter().sum();
    println!("{}", s);
}
