DSP = noise_gate.dsp
NAME = noise_gate

.PHONY: all check juce svg clean

all: check

# Verifica sintaxis y compila a C++ básico
check:
	faust -wall -double $(DSP) -o $(NAME).cpp
	@echo "✓ Faust syntax and C++ code generation successful."

# Genera proyecto JUCE usando faust2juce
juce:
	faust2juce $(DSP)
	@echo "✓ JUCE project generated successfully."

# Genera diagramas de bloques en formato SVG
svg:
	faust2svg $(DSP)
	@echo "✓ Faust block diagram SVG generated."

# Limpieza de temporales generados
clean:
	rm -rf $(NAME).cpp $(NAME)-svg $(NAME) $(NAME)-juce Builds JuceLibraryCode
