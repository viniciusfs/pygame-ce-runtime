.PHONY: build-runtime build-package clean

build-runtime:
	docker compose up

build-package:
	cp build/pygame-ce_2.5.6_python_3.12.8.squashfs example/MyGame/runtime/pygame-ce_2.5.6_python_3.12.8.squashfs
	cd example && zip -r ../build/MyGame.zip MyGame MyGame.sh && cd -
	rm example/MyGame/runtime/pygame-ce_2.5.6_python_3.12.8.squashfs

clean:
	rm -rf build/*
