// Scenarios C and D: fill a buffer of n numbers, then sum all of it r times (arguments: r n)
package main

import (
	"fmt"
	"os"
	"strconv"
)

func main() {
	r := 1
	if len(os.Args) > 1 {
		r, _ = strconv.Atoi(os.Args[1])
	}
	n := 10000000
	if len(os.Args) > 2 {
		n, _ = strconv.Atoi(os.Args[2])
	}
	p := make([]int64, n)
	for i := range p {
		p[i] = int64(i & 1023)
	}
	var t int64
	for q := 0; q < r; q++ {
		p[q]++
		var s int64
		for _, x := range p {
			s += x
		}
		t += s
	}
	fmt.Println(t)
}
