package main

import (
	"flag"
	"fmt"
	"math"
)

func deg2Rad(deg float64) float64 {
	return deg / 180 * math.Pi
}

func getStack(ha, hl, fl, fo, bb float64) float64 {
	return math.Sin(deg2Rad(ha)) * (hl + fl - fo * math.Cos(deg2Rad(ha))) + bb
}

func getReach(tt, stack, sa float64) float64 {
	return tt - stack * math.Tan(deg2Rad(90 - sa))
}

func main() {
	fmt.Println(`
This program calculates bike frame stack and reach values using head tube angle,
head tube length, fork length, fork offset, toptube length, seat tube angle and
bottom bracket drop.
`)

	ha := flag.Float64("ha", 0, "Head tube angle in degrees.")
	hl := flag.Float64("hl", 0, "Length of the head tube in mm.")
	fl := flag.Float64("fl", 0, "Fork axle to crown length in mm.")
	fo := flag.Float64("fo", 0, "Fork offset in mm.")
	tt := flag.Float64("tt", 0, "Top tube length in mm.")
	sa := flag.Float64("sa", 0, "Seat tube length in degrees.")
	bb := flag.Float64("bb", 0, "Bottom bracket drop in mm.")

	flag.Parse()

	stack := getStack(*ha, *hl, *fl, *fo, *bb)
	reach := getReach(*tt, stack, *sa)

	output := fmt.Sprintf("Stack = %.1f\nReach = %.1f\n", stack, reach)
	fmt.Println(output)
}
