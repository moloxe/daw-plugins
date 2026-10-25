# DAW Plugins (FAUST + JUCE + Xcode)

Colección de plugins y procesadores de señal de audio desarrollados en [FAUST](https://faust.grame.fr/) y compilados localmente a **VST3 / AU** mediante [JUCE](https://juce.com/) y **Xcode** en macOS.

---

## Plugins

### 1. [Noise Gate](noise-gate/)
Noise Gate estéreo con:
- Detección de envolvente **RMS** enlazada estéreo ($\sqrt{(L^2 + R^2)/2}$).
- Controles: **Threshold (dB)**, **Attack (ms)**, **Hold (ms)**, **Release (ms)** y **Floor (dB)**.
- Operación libre de clicks (`si.smoo`, generador de envolvente continuo $C^1$ y retención precisa en muestras).
- Medidores visuales integrados de Input RMS y Gate Gain.
- **Interfaz gráfica moderna inspirada en Ableton Live**: formato horizontal compacto (~450 × 175 px), paleta oscura de alto contraste, perillas con arcos cyan (`#00D2FF`) y medidores VU optimizados.

---

## Requisitos Previos

- **macOS** con Apple Silicon o Intel.
- **Homebrew** y **FAUST**:
  ```bash
  brew install faust
  ```
- **Xcode** (desde Mac App Store o Apple Developer).
- **JUCE 9** ubicado en la raíz del repositorio (`daw-plugins/JUCE/`).

---

## Flujo de Compilación Local

### 1. Generar el Proyecto JUCE y Xcode
Entra a la carpeta del plugin y ejecuta:
```bash
cd noise-gate
make juce
```
El `Makefile` automatiza:
- Conversión de `noise_gate.dsp` a C++ mediante `faust2juce` apuntando a `daw-plugins/JUCE/modules`.
- Configuración de compatibilidad con **macOS 13.0+** (`MACOSX_DEPLOYMENT_TARGET = 13.0`).
- Aplicación automática del tema oscuro compacto estilo Ableton (`scripts/patch_juce_gui.py`).
- Parche automático para la API gráfica de **JUCE 9** (`juce::GlyphArrangement::getStringWidthInt`).
- Resolución automática de dependencias de módulos (`juce_audio_processors_headless`) y generación del proyecto Xcode con `Projucer --resave --fix-missing-dependencies`.

### 2. Compilar e Instalar (desde Terminal o Xcode)

#### Opción A: Directamente desde Terminal (Recomendado)
Desde la carpeta `noise-gate/`:
```bash
make build       # Compila VST3 y lo instala en ~/Library/Audio/Plug-Ins/VST3/
make build-au    # Compila AU y lo instala en ~/Library/Audio/Plug-Ins/Components/
```

#### Opción B: Desde Xcode GUI
Abre el proyecto generado:
```bash
open noise_gate/Builds/MacOSX/noise_gate.xcodeproj
```
1. En la barra superior de Xcode, selecciona el esquema **`noise_gate - VST3`** (o **`noise_gate - AU`**).
2. Presiona **`Cmd + B`** (o *Product > Build*).
3. Xcode compilará y copiará el binario resultante automáticamente a las carpetas del sistema.

---

## Uso en Ableton Live 12 Lite

1. Abre **Ableton Live 12 Lite**.
2. Ve a **Live > Ajustes...** (`Cmd + ,`) > pestaña **Plug-Ins**.
3. Activa las opciones para VST3 y/o Audio Units y haz clic en **Rescan Plugins** (mantén presionada la tecla `Option` al hacer clic para forzar un escaneo profundo).
4. En el navegador lateral de Live, ve a **Plug-Ins** > **VST3** o **Audio Units** y arrastra **`noise_gate`** a tu pista.

---

## Comandos Útiles del Makefile

Desde la carpeta `noise-gate/`:
- `make check`: Valida la sintaxis FAUST y compila a C++ en consola.
- `make juce`: Genera y actualiza el proyecto JUCE / Xcode con todas las dependencias y el tema Ableton.
- `make build`: Compila el VST3 con `xcodebuild` y lo instala en el sistema.
- `make build-au`: Compila el AU con `xcodebuild` y lo instala en el sistema.
- `make build-standalone`: Compila y genera la aplicación Standalone de prueba.
- `make svg`: Genera los diagramas de bloques del algoritmo DSP en SVG.
- `make clean`: Limpia los artefactos generados.
