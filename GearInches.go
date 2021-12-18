package main

import "fmt"

func calculate(frontcog, rearcog, wheelsize float32) float32 {
	return frontcog / rearcog * wheelsize
}

func main() {
	var frontcog float32
	var rearcog float32
	var wheelsize float32

	fmt.Print("Frontcog size: ")
	fmt.Scan(&frontcog)
	fmt.Print("Rearcog size: ")
	fmt.Scan(&rearcog)
	fmt.Print("Wheelsize (inches): ")
	fmt.Scan(&wheelsize)

	gearInches := calculate(frontcog, rearcog, wheelsize)
	output := fmt.Sprintf("Gear inches = %.1f", gearInches)
	fmt.Println(output)
}
