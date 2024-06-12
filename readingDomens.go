package main

import (
	"bufio"
	"fmt"
	"io/fs"
	"os"
	"path/filepath"
	"regexp"
	"strings"
)

func main() {

	// Путь к каталогу, который нужно сканировать
	dirPath := "/Users/rusk/PycharmProjects/master/mosru_nginx/"

	// Проверяем, существует ли каталог
	if _, err := os.Stat(dirPath); os.IsNotExist(err) {
		fmt.Println("Каталог не найден:", dirPath)
		return
	}

	// Ищем файл site.yml в каталоге
	var siteYmlPath string
	err := filepath.WalkDir(dirPath, func(path string, d fs.DirEntry, err error) error {
		if err != nil {
			return err
		}
		if d.IsDir() {
			return nil
		}
		if d.Name() == "www.mos.ru_9443.yml" {
			siteYmlPath = path
			return fs.SkipDir // Прекращаем обход после нахождения файла
		}
		return nil
	})
	if err != nil {
		fmt.Println("Ошибка при обходе каталога:", err)
		return
	}
	if siteYmlPath == "" {
		fmt.Println("Файл site.yml не найден в каталоге:", dirPath)
		return
	}

	// Открываем файл для чтения
	file, err := os.Open(siteYmlPath)
	if err != nil {
		fmt.Println("Ошибка при открытии файла:", err)
		return
	}
	defer file.Close()

	// Создаем сканер для чтения файла построчно
	scanner := bufio.NewScanner(file)

	// Регулярное выражение для поиска URL после proxy_pass и до первого символа / или $
	re := regexp.MustCompile(`proxy_pass\s+(http[s]?://[^/]+|http[s]?://[^$]+)`)

	// Проходим по каждой строке файла
	for scanner.Scan() {
		line := scanner.Text()
		matches := re.FindStringSubmatch(line)
		if len(matches) > 1 {
			// Извлекаем URL и обрезаем http:// или https://
			url := strings.TrimPrefix(matches[1], "http://")
			url = strings.TrimPrefix(url, "https://")
			// Выводим обрезанный URL
			fmt.Println(url)

		}
	}

	if err := scanner.Err(); err != nil {
		fmt.Println("Ошибка при чтении файла:", err)
	}

}
