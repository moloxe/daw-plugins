# ==============================================================================
# DAW Plugins Common Makefile (FAUST + JUCE 9 + Xcode)
# ==============================================================================
# Included by individual plugin Makefiles:
#
#   DSP  = <name>.dsp
#   NAME = <name>
#   include ../scripts/plugin_common.mk
# ==============================================================================

ROOT_DIR     := $(abspath $(dir $(lastword $(MAKEFILE_LIST)))/..)
JUCE_DIR     := $(ROOT_DIR)/JUCE
JUCE_MODULES := $(JUCE_DIR)/modules
PROJUCER     := $(JUCE_DIR)/Projucer.app/Contents/MacOS/Projucer
PATCH_SCRIPT := $(ROOT_DIR)/scripts/patch_juce_gui.py

.PHONY: all check juce build build-au build-standalone svg clean

all: check

# 1. Verifica sintaxis FAUST y compila a C++ básico
check:
	faust -wall -double $(DSP) -o $(NAME).cpp
	@echo "✓ Faust syntax and C++ code generation successful."

# 2. Genera proyecto JUCE usando faust2juce, aplica el parche de UI Ableton Dark y actualiza con Projucer
juce:
	faust2juce -jucemodulesdir $(JUCE_MODULES) $(DSP)
	@python3 "$(PATCH_SCRIPT)" $(NAME)
	@if [ -f "$(PROJUCER)" ]; then \
		"$(PROJUCER)" --resave $(NAME)/$(NAME).jucer --fix-missing-dependencies; \
		echo "✓ JUCE 9 & Xcode project updated successfully with Projucer (Ableton Dark theme)."; \
	else \
		echo "✓ JUCE project generated successfully."; \
	fi

# 3. Compila el plugin VST3 y lo instala automáticamente en ~/Library/Audio/Plug-Ins/VST3/
build:
	xcodebuild -project $(NAME)/Builds/MacOSX/$(NAME).xcodeproj -scheme "$(NAME) - VST3" -configuration Release build

# 4. Compila el plugin AU (Audio Unit) en ~/Library/Audio/Plug-Ins/Components/
build-au:
	xcodebuild -project $(NAME)/Builds/MacOSX/$(NAME).xcodeproj -scheme "$(NAME) - AU" -configuration Release build

# 5. Compila la versión Standalone de prueba
build-standalone:
	xcodebuild -project $(NAME)/Builds/MacOSX/$(NAME).xcodeproj -scheme "$(NAME) - Standalone Plugin" -configuration Release build

# 6. Genera diagramas de bloques en formato SVG
svg:
	faust2svg $(DSP)
	@echo "✓ Faust block diagram SVG generated."

# 7. Limpieza de artefactos generados
clean:
	rm -rf $(NAME).cpp $(NAME)-svg $(NAME) $(NAME)-juce Builds JuceLibraryCode
