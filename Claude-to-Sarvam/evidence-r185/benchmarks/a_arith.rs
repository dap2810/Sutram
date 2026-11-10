// Scenario A: 10,000,000 passes of s = s + i * 2
fn main() {
    let mut s: i64 = 0;
    for i in 0..10_000_000i64 {
        s += i * 2;
    }
    println!("{}", s);
}
