package main

import (
	"fmt"
	"math/rand"
	"time"
)

func generatePassword(length int) string {
	rand.Seed(time.Now().UnixNano())

	charset := "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+{}:<>?|"

	password := make([]byte, length)
	for i := range password {
		password[i] = charset[rand.Intn(len(charset))]
	}

	return string(password)
}

func main() {
	passwordLength := 16
	password := generatePassword(passwordLength)
	fmt.Println("Generated Password:", password)
}
