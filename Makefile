.PHONY: install run build-appimage build-windows clean help

help:
	@echo "Linked List Snake - Build & Run Targets"
	@echo "======================================="
	@echo "  make install       - Install dependencies"
	@echo "  make run           - Run the game directly"
	@echo "  make build-appimage - Build Linux AppImage (requires linuxdeploy or appimagetool)"
	@echo "  make build-windows  - Build Windows executable (requires PyInstaller)"
	@echo "  make clean         - Remove build artifacts"

install:
	pip install -r requirements.txt

run:
	python3 main.py

build-appimage:
	bash build_appimage_linuxdeploy.sh

build-windows:
	python3 build_windows_exe.py

build-all: build-appimage build-windows
	@echo "All builds complete!"

clean:
	rm -rf build/ dist/ *.spec *.AppImage
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
