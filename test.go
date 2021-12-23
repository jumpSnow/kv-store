func unzipFiles(dest string, zipFile string) (string, error) {
	reader, err := zip.OpenReader(zipFile)
	if err != nil {
		return "", errors.New("error")
	}
	defer reader.Close()
	for _, file := range reader.File {
		path := filepath.Join(dest, file.Name)
		if file.FileInfo().IsDir() {
			os.MkdirAll(path, file.Mode())
		} else {
			fileReader, err := file.Open()
			if err != nil {
				return "", errors.New("fileReader error")
			}
			defer fileReader.Close()
			targetFile, err := os.OpenFile(path, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, file.Mode())
			if err != nil {
				return "", errors.New("targetFile open error")
			}
			defer targetFile.Close()

			if _, err := io.Copy(targetFile, fileReader); err != nil {
				return "", errors.New("Copy error")
			}
		}
	}
	return dest, nil
}
