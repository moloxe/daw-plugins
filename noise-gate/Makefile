DSP = noise_gate.dsp
NAME = noise_gate
JUCE_DIR = $(CURDIR)/../JUCE
JUCE_MODULES = $(JUCE_DIR)/modules
PROJUCER = $(JUCE_DIR)/Projucer.app/Contents/MacOS/Projucer

.PHONY: all check juce build build-au build-standalone svg clean

all: check

# Verifica sintaxis y compila a C++ básico
check:
	faust -wall -double $(DSP) -o $(NAME).cpp
	@echo "✓ Faust syntax and C++ code generation successful."

# Genera proyecto JUCE usando faust2juce y adapta compatibilidad con JUCE 9 + macOS 13.0 + tema compacto Ableton
juce:
	faust2juce -jucemodulesdir $(JUCE_MODULES) $(DSP)
	@python3 scripts/patch_juce_gui.py $(NAME)
	@if [ -f "$(PROJUCER)" ]; then \
		"$(PROJUCER)" --resave $(NAME)/$(NAME).jucer --fix-missing-dependencies; \
		echo "✓ JUCE 9 & Xcode project updated successfully with Projucer (Ableton Dark theme)."; \
	else \
		echo "✓ JUCE project generated successfully."; \
	fi

# Compila el plugin VST3 y lo instala automáticamente en ~/Library/Audio/Plug-Ins/VST3/
build:
	xcodebuild -project $(NAME)/Builds/MacOSX/$(NAME).xcodeproj -scheme "$(NAME) - VST3" -configuration Release build

# Compila el plugin AU (Audio Unit) en ~/Library/Audio/Plug-Ins/Components/
build-au:
	xcodebuild -project $(NAME)/Builds/MacOSX/$(NAME).xcodeproj -scheme "$(NAME) - AU" -configuration Release build

# Compila la versión Standalone de prueba
build-standalone:
	xcodebuild -project $(NAME)/Builds/MacOSX/$(NAME).xcodeproj -scheme "$(NAME) - Standalone Plugin" -configuration Release build

# Genera diagramas de bloques en formato SVG
svg:
	faust2svg $(DSP)
	@echo "✓ Faust block diagram SVG generated."

# Limpieza de temporales generados
clean:
	rm -rf $(NAME).cpp $(NAME)-svg $(NAME) $(NAME)-juce Builds JuceLibraryCode
