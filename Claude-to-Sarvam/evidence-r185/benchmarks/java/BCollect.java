// Scenario B: build a collection of 1,000,000 numbers, then sum it - ArrayList<Long>, the usual
// growing collection; every number in it is an object.
import java.util.ArrayList;

public class BCollect {
    public static void main(String[] args) {
        ArrayList<Long> v = new ArrayList<>();
        for (long i = 0; i < 1000000L; i++) {
            v.add(i);
        }
        long s = 0;
        for (long x : v) {
            s += x;
        }
        System.out.println(s);
    }
}
