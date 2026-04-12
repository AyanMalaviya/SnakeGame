.PHONY: install run build-appimage clean help

help:
	@echo "Hizzz Snake - Build & Run Targets"
	@echo "======================================="
	@echo "  make install        - Install dependencies"
	@echo "  make run            - Run launcher (single + local multiplayer)"
	@echo "  make build-appimage - Build Linux AppImage"
	@echo "  make clean          - Remove build artifacts"

install:
	pip install -r requirements.txt

run:
	python3 main_multiplayer.py

build-appimage:
	bash build_appimage_linuxdeploy.sh

clean:
	rm -rf build/ dist/ *.spec *.AppImage
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
