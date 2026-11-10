// Scenario A2: 10,000,000 passes of s = (s + i * 2) ^ (s >> 3)
public class A2ArithDependent {
    public static void main(String[] args) {
        long s = 0;
        for (long i = 0; i < 10000000L; i++) {
            s = (s + i * 2) ^ (s >> 3);
        }
        System.out.println(s);
    }
}
