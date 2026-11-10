// Scenario A2: 10,000,000 passes of s = (s + i * 2) ^ (s >> 3)
package main

import "fmt"

func main() {
	var s int64
	for i := int64(0); i < 10000000; i++ {
		s = (s + i*2) ^ (s >> 3)
	}
	fmt.Println(s)
}
