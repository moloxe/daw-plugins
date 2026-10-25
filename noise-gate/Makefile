DSP = noise_gate.dsp
NAME = noise_gate
JUCE_DIR = $(CURDIR)/../JUCE
JUCE_MODULES = $(JUCE_DIR)/modules
PROJUCER = $(JUCE_DIR)/Projucer.app/Contents/MacOS/Projucer

.PHONY: all check juce svg clean

all: check

# Verifica sintaxis y compila a C++ básico
check:
	faust -wall -double $(DSP) -o $(NAME).cpp
	@echo "✓ Faust syntax and C++ code generation successful."

# Genera proyecto JUCE usando faust2juce y adapta compatibilidad con JUCE 9 + macOS 13.0
juce:
	faust2juce -jucemodulesdir $(JUCE_MODULES) $(DSP)
	@python3 -c 'p="$(NAME)/$(NAME).jucer"; t=open(p).read(); t=t.replace("targetName=\"$(NAME)\"/>", "targetName=\"$(NAME)\" osxCompatibility=\"13.0 SDK\"/>"); open(p,"w").write(t)'
	@python3 -c 'p="$(NAME)/FaustPluginProcessor.cpp"; t=open(p).read(); t=t.replace("juce::Font().getStringWidth(", "juce::GlyphArrangement::getStringWidthInt(juce::Font(juce::FontOptions()), "); open(p,"w").write(t)'
	@if [ -f "$(PROJUCER)" ]; then \
		"$(PROJUCER)" --resave $(NAME)/$(NAME).jucer --fix-missing-dependencies; \
		echo "✓ JUCE 9 & Xcode project updated successfully with Projucer (macOS 13.0+)."; \
	else \
		echo "✓ JUCE project generated successfully."; \
	fi

# Genera diagramas de bloques en formato SVG
svg:
	faust2svg $(DSP)
	@echo "✓ Faust block diagram SVG generated."

# Limpieza de temporales generados
clean:
	rm -rf $(NAME).cpp $(NAME)-svg $(NAME) $(NAME)-juce Builds JuceLibraryCode
