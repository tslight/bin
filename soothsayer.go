package main

import (
	"fmt"
	"log"
	"os"
	"os/exec"

	"github.com/gdamore/tcell/v2"
)

func drawText(s tcell.Screen, x1, y1, x2, y2 int, style tcell.Style, text string) {
	row := y1
	col := x1
	for _, r := range []rune(text) {
		s.SetContent(col, row, r, nil, style)
		col++
		if col >= x2 {
			row++
			col = x1
		}
		if row > y2 {
			break
		}
	}
}

func drawBox(s tcell.Screen, x1, y1, x2, y2 int, style tcell.Style, text string) {
	if y2 < y1 {
		y1, y2 = y2, y1
	}
	if x2 < x1 {
		x1, x2 = x2, x1
	}

	// Fill background
	for row := y1; row <= y2; row++ {
		for col := x1; col <= x2; col++ {
			s.SetContent(col, row, ' ', nil, style)
		}
	}

	drawText(s, x1, y1, x2, y2, style, text)
}

func getFortune() string {
	out, err := exec.Command("fortune").Output()
	if err != nil {
		log.Fatal(err)
	}
	return fmt.Sprintf("%s", out)
}

func main() {
	headerStyle := tcell.StyleDefault.
		Foreground(tcell.ColorWhite).
		Background(tcell.ColorDarkBlue)
	boxStyle := tcell.StyleDefault.
		Foreground(tcell.ColorDefault).
		Background(tcell.ColorDefault)
	footerStyle := tcell.StyleDefault.
		Foreground(tcell.ColorWhite).
		Background(tcell.ColorDarkBlue)

	// Initialize screen
	s, err := tcell.NewScreen()
	if err != nil {
		log.Fatalf("%+v", err)
	}
	if err := s.Init(); err != nil {
		log.Fatalf("%+v", err)
	}

	s.EnableMouse()
	s.EnablePaste()
	s.Clear()

	// Event loop
	quit := func() {
		s.Fini()
		os.Exit(0)
	}

	fortune := getFortune()

	for {
		// Update screen
		s.Show()

		// Poll event
		ev := s.PollEvent()
		w, h := s.Size()
		drawBox(s, 0, 0, w, 1, headerStyle.Bold(true), "GET YOUR FORTUNES HERE!")
		drawBox(s, 0, 1, w, h-2, boxStyle, fortune)
		drawBox(
			s, 0, h-1, w, h,
			footerStyle.Bold(true),
			"[SPC] or [n] for more fortunes, [q] or [ESC] to quit",
		)

		// Process event
		switch ev := ev.(type) {
		// case *tcell.EventResize:
		//  s.Sync()
		case *tcell.EventKey:
			if ev.Key() == tcell.KeyEscape || ev.Rune() == 'q' {
				quit()
			}
			if ev.Rune() == ' ' || ev.Rune() == 'n' {
				fortune = getFortune()
			}
		}
	}
}
