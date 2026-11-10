// Scenario B: build a collection of 1,000,000 numbers, then sum it - a slice and append
package main

import "fmt"

func main() {
	var v []int64
	for i := int64(0); i < 1000000; i++ {
		v = append(v, i)
	}
	var s int64
	for _, x := range v {
		s += x
	}
	fmt.Println(s)
}
