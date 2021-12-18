package main

import (
	"flag"
	"fmt"
)

func interactive(prompt string) float64 {
	fmt.Print(prompt, ": ")
	var result float64
	fmt.Scan(&result)
	return result
}

func calculate(frontcog, rearcog, wheelsize float64) float64 {
	if frontcog == 0 {
		frontcog = interactive("Frontcog")
	} else {
		fmt.Println("Frontcog:", frontcog)
	}
	if rearcog == 0 {
		rearcog = interactive("Rearcog")
	} else {
		fmt.Println("Rearcog:", rearcog)
	}
	if wheelsize == 0 {
		wheelsize = interactive("Wheelsize")
	} else {
		fmt.Println("Wheelsize:", wheelsize)
	}
	return frontcog / rearcog * wheelsize
}

func main() {
	fmt.Println(`
This program calculates gear inches given the number of teeth on the front cog,
the number of teeth on the rear cog and the diameter of the wheels in inches.

55" is the typical size for a BMX with either 44/16 or 25/9.
`)

	frontcog := flag.Float64(
		"frontcog", 0, "Number of teeth on the front sprocket.",
	)
	rearcog := flag.Float64(
		"rearcog", 0, "Number of teeth on the rear sprocket.",
	)
	wheelsize := flag.Float64(
		"wheelsize", 0, "Diameter of wheels in inches.",
	)

	flag.Parse()

	gearInches := calculate(*frontcog, *rearcog, *wheelsize)

	output := fmt.Sprintf("\nGear inches = %.1f\n", gearInches)
	fmt.Println(output)
}
