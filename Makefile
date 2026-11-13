CMAKE ?= cmake
BUILD_DIR ?= build
CONFIG ?= Debug
JOBS ?= 2
CMAKE_ARGS ?=

.PHONY: all configure build test profile clean
all: build

configure:
	"$(CMAKE)" -S . -B "$(BUILD_DIR)" -DCMAKE_BUILD_TYPE="$(CONFIG)" $(CMAKE_ARGS)

build: configure
	"$(CMAKE)" --build "$(BUILD_DIR)" --config "$(CONFIG)" --parallel "$(JOBS)"

test: build
	"$(CMAKE)" --build "$(BUILD_DIR)" --config "$(CONFIG)" --target check

profile: configure
	"$(CMAKE)" --build "$(BUILD_DIR)" --config "$(CONFIG)" --target hammond_profile

# Use the generated build's clean target; never recursively delete a user path.
clean:
	@if [ -f "$(BUILD_DIR)/CMakeCache.txt" ]; then \
		"$(CMAKE)" --build "$(BUILD_DIR)" --config "$(CONFIG)" --target clean; \
	else \
		printf '%s\n' 'No configured build to clean.'; \
	fi
