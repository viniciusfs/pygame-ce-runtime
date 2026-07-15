include build-config

RUNTIME := pygame-ce_$(PYGAME_VERSION)_python_$(PYTHON_VERSION)
SQUASHFS := build/$(RUNTIME).squashfs

.PHONY: build-runtime build-package clean

build-runtime:
	docker compose --env-file build-config up

build-package:
	@set -e; \
	if [ ! -f "$(SQUASHFS)" ]; then \
	  echo "error: $(SQUASHFS) not found, run 'make build-runtime' first" >&2; \
	  exit 1; \
	fi; \
	dest=example/MyGame/runtime/$(RUNTIME).squashfs; \
	trap 'rm -f "$$dest"' EXIT; \
	mkdir -p example/MyGame/runtime; \
	cp "$(SQUASHFS)" "$$dest"; \
	(cd example && zip -r ../build/MyGame.zip MyGame MyGame.sh)

clean:
	rm -rf build/*
	find . -type d -name "__pycache__" | xargs rm -rf
	find . -type f -name "*.log" | xargs rm
	docker compose down
