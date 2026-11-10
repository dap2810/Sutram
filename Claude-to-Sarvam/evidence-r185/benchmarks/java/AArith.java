// Scenario A: 10,000,000 passes of s = s + i * 2
public class AArith {
    public static void main(String[] args) {
        long s = 0;
        for (long i = 0; i < 10000000L; i++) {
            s = s + i * 2;
        }
        System.out.println(s);
    }
}
