# DAW Plugins (FAUST + JUCE + Xcode)

Colección estandarizada de plugins y procesadores de señal de audio desarrollados en [FAUST](https://faust.grame.fr/) y compilados localmente a **VST3 / AU** mediante [JUCE](https://juce.com/) y **Xcode** en macOS.

---

## Plugins

> 📖 **Guía Completa de Uso y Parámetros**: Consulta el manual detallado [docs/PLUGIN-INSTRUCTIONS.md](docs/PLUGIN-INSTRUCTIONS.md) para conocer las instrucciones de uso paso a paso, calibración en sala, flujo de señal en tu DAW, tablas completas de parámetros, lectura de medidores y presets recomendados.

### 1. [Noise Gate](noise-gate/)
Noise Gate estéreo con:
- Detección de envolvente **RMS** enlazada estéreo ($\sqrt{(L^2 + R^2)/2}$).
- Controles: **Threshold (dB)**, **Attack (ms)**, **Hold (ms)**, **Release (ms)** y **Floor (dB)**.
- Operación libre de clicks (`si.smoo`, generador de envolvente continuo $C^1$ y retención precisa en muestras).
- Medidores visuales integrados de Input RMS y Gate Gain.
- **Interfaz gráfica moderna inspirada en Ableton Live**: formato horizontal compacto (~450 × 196 px), paleta oscura de alto contraste, perillas con arcos cyan (`#00D2FF`) y medidores VU optimizados.

### 2. [Feedback Suppressor](feedback-suppressor/)
Supresor automático y quirúrgico de acople acústico (*feedback / Larsen*) en milisegundos con:
- **Detección analítica de prominencia tonal**: Monitoreo en 8 bandas críticas (`160 Hz` a `10 kHz`) que evalúa la relación entre energía resonante ultra estrecha y energía vecina para destruir pitidos de acople sin alterar el brillo ni el tono natural de la voz o instrumento.
- **Botón `Calibrate`**: Escaneo y memorización rápida (*room resonance latch*) de los filtros notch necesarios en la habitación o escenario, con botón `Reset` para limpiar la memoria instantáneamente.
- **Controles simplificados**: **Calibrate**, **Reset**, **Sensitivity (dB)**, **Max Cut (dB)**, **Sharpness (Q)** y **Gain (dB)**.
- **Visualizador de Supresión de Acople**: Panel gráfico con 8 medidores de corte descendentes desde $0\text{ dB}$ en color Cyan Ableton (`#00D2FF`) que reflejan la profundidad de la muesca quirúrgica en tiempo real, junto con medidor RMS de entrada.


---

## Arquitectura y Estándar del Repositorio

El repositorio cuenta con una infraestructura unificada para crear y modificar plugins manteniendo coherencia visual y técnica:

```text
daw-plugins/
├── AGENTS.md                   # Reglas universales obligatorias para el agente AI
├── README.md                   # Documentación general del repositorio
├── docs/
│   └── PLUGIN-INSTRUCTIONS.md  # Manual completo de uso, calibración y presets
├── .gitignore                  # Exclusión automática de binarios y fuentes JUCE generados
├── JUCE/                       # Instalación de JUCE 9 (módulos y Projucer.app)
├── scripts/
│   ├── patch_juce_gui.py       # Parche central de UI (Ableton Dark, fuentes JUCE 9, macOS 13.0+)
│   └── plugin_common.mk        # Makefile compartido con todas las metas de compilación
├── .agents/skills/
│   └── faust-juce-plugin/      # Skill especializada de Antigravity para creación de plugins
├── noise-gate/                 # Stereo RMS Noise Gate
│   ├── noise_gate.dsp          # Código FAUST del procesador DSP
│   └── Makefile                # Makefile declarativo (solo 3 líneas)
└── feedback-suppressor/        # Automatic Surgical Feedback Suppressor
    ├── feedback_suppressor.dsp # Código FAUST del procesador DSP
    └── Makefile                # Makefile declarativo (solo 3 líneas)
```

### Cómo Crear un Nuevo Plugin en 3 Pasos

1. **Crea el subdirectorio**:
   ```bash
   mkdir my-plugin
   ```
2. **Crea su `Makefile`**:
   ```makefile
   DSP  = my_plugin.dsp
   NAME = my_plugin

   include ../scripts/plugin_common.mk
   ```
3. **Escribe el código FAUST (`my_plugin.dsp`)** siguiendo el layout horizontal `hgroup` y ejecuta:
   ```bash
   cd my-plugin
   make check    # Valida sintaxis DSP
   make juce     # Genera código C++ JUCE con tema oscuro Ableton
   make build    # Compila e instala VST3
   make build-au # Compila e instala AU
   ```

Consulta el documento [AGENTS.md](AGENTS.md) para conocer las normas de DSP, colores y dimensiones obligatorias.

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
Entra a la carpeta del plugin deseado y ejecuta:
```bash
cd noise-gate
make juce
```
El script automatiza:
- Conversión de `.dsp` a C++ mediante `faust2juce` apuntando a `daw-plugins/JUCE/modules`.
- Configuración de compatibilidad con **macOS 13.0+** (`MACOSX_DEPLOYMENT_TARGET = 13.0`).
- Aplicación del tema oscuro compacto estilo Ableton (`scripts/patch_juce_gui.py`).
- Parche para la API gráfica de fuentes de **JUCE 9** (`juce::GlyphArrangement::getStringWidthInt`).
- Resolución de dependencias (`juce_audio_processors_headless`) y regeneración de Xcode con `Projucer --resave --fix-missing-dependencies`.

### 2. Compilar e Instalar (desde Terminal o Xcode)

#### Opción A: Directamente desde Terminal (Recomendado)
Desde la carpeta del plugin:
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
4. En el navegador lateral de Live, ve a **Plug-Ins** > **VST3** o **Audio Units** y arrastra el plugin a tu pista.

---

## Comandos Útiles del Makefile

Desde la carpeta de cualquier plugin:
- `make check`: Valida la sintaxis FAUST y compila a C++ en consola.
- `make juce`: Genera y actualiza el proyecto JUCE / Xcode con todas las dependencias y el tema Ableton.
- `make build`: Compila el VST3 con `xcodebuild` y lo instala en el sistema.
- `make build-au`: Compila el AU con `xcodebuild` y lo instala en el sistema.
- `make build-standalone`: Compila y genera la aplicación Standalone de prueba.
- `make svg`: Genera los diagramas de bloques del algoritmo DSP en SVG.
- `make clean`: Limpia los artefactos generados.
