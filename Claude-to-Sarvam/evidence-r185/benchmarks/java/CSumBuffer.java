// Scenarios C and D: fill a buffer of n numbers, then sum all of it r times (arguments: r n)
public class CSumBuffer {
    public static void main(String[] args) {
        int r = args.length > 0 ? Integer.parseInt(args[0]) : 1;
        int n = args.length > 1 ? Integer.parseInt(args[1]) : 10000000;
        long[] p = new long[n];
        for (int i = 0; i < p.length; i++) {
            p[i] = i & 1023;
        }
        long t = 0;
        for (int q = 0; q < r; q++) {
            p[q] += 1;
            long s = 0;
            for (long x : p) {
                s += x;
            }
            t += s;
        }
        System.out.println(t);
    }
}
