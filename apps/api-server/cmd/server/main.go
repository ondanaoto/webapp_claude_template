package main

import (
	"log/slog"
	"os"

)

func main() {
	slog.SetDefault(slog.New(slog.NewJSONHandler(os.Stdout, nil)))

	if err := run(); err != nil {
		slog.Error("server failed", slog.String("error", err.Error()))
		os.Exit(1)
	}
}

func run() error {
	// TODO: Implement the server logic
	return nil
}
