# DAW Plugins (FAUST + JUCE)

Colección de plugins y procesadores de señal de audio desarrollados en [FAUST](https://faust.grame.fr/) con exportación a [JUCE](https://juce.com/) y soporte directo para [Faust IDE](https://faustide.grame.fr/).

---

## Plugins

### 1. [Noise Gate](noise-gate/)
Noise Gate estéreo de alta calidad con:
- Detección de envolvente **RMS** enlazada estéreo.
- Parámetros: **Threshold (dB)**, **Attack (ms)**, **Hold (ms)**, **Release (ms)** y **Floor (dB)**.
- Transiciones continuas y libres de clicks (interpolación con `si.smoo` y generador de envolvente de primer orden con temporizador de retención en muestras).
- Medidores visuales de RMS de entrada y reducción de ganancia integrados.

---

## Flujo de Trabajo

### Vía Faust IDE (Web)
1. Abre [Faust IDE](https://faustide.grame.fr/).
2. Arrastra el archivo `.dsp` (por ejemplo, [noise-gate/noise_gate.dsp](noise-gate/noise_gate.dsp)).
3. Puedes probarlo directamente con audio en vivo, visualizar los diagramas de bloques y exportar a WebAudio, C++, VST, AU, etc.

### Vía CLI Local (faust2juce)
Requisitos previos:
- Faust instalado (`brew install faust`).
- JUCE / Projucer (opcional para compilar los binarios finales VST3/AU/Standalone).

Comandos en cada subdirectorio de plugin (ej. `cd noise-gate`):
- `make check`: Valida la sintaxis del archivo DSP y compila a C++.
- `make juce`: Ejecuta `faust2juce` generando la estructura de proyecto JUCE (`.jucer` y código C++ de procesamiento).
- `make svg`: Genera diagramas de bloques en SVG para inspeccionar el flujo de señal.
- `make clean`: Limpia artefactos generados.
