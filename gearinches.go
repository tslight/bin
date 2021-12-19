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

func calculate(fc, rc, ws float64) float64 {
	if fc == 0 {
		fc = interactive("Frontcog")
	} else {
		fmt.Println("Frontcog:", fc)
	}
	if rc == 0 {
		rc = interactive("Rearcog")
	} else {
		fmt.Println("Rearcog:", rc)
	}
	if ws == 0 {
		ws = interactive("Wheelsize")
	} else {
		fmt.Println("Wheelsize:", ws)
	}
	return fc / rc * ws
}

func main() {
	fmt.Println(`
This program calculates gear inches given the number of teeth on the front cog,
the number of teeth on the rear cog and the diameter of the wheels in inches.

55" is the typical size for a BMX with either 44/16 or 25/9.
`)

	fc := flag.Float64("fc", 0, "Number of teeth on the front sprocket.")
	rc := flag.Float64("rc", 0, "Number of teeth on the rear sprocket.")
	ws := flag.Float64("ws", 0, "Diameter of wheels in inches.")

	flag.Parse()

	gearInches := calculate(*fc, *rc, *ws)

	output := fmt.Sprintf("\nGear inches = %.1f\n", gearInches)
	fmt.Println(output)
}
