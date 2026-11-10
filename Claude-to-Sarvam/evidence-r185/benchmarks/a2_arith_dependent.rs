// Scenario A2: 10,000,000 passes of s = (s + i * 2) ^ (s >> 3)
fn main() {
    let mut s: i64 = 0;
    for i in 0..10_000_000i64 {
        s = s.wrapping_add(i * 2) ^ (s >> 3);
    }
    println!("{}", s);
}
