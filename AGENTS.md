# Guía y Estándares de Desarrollo para DAW Plugins (FAUST + JUCE 9 + macOS)

Este documento define el estándar obligatorio y universal para la creación, modificación, diseño visual, compilación y verificación de plugins de audio en este repositorio. Cualquier agente o desarrollador que opere en este workspace debe seguir estrictamente estas directrices.

---

## 1. Arquitectura del Repositorio

- **Estructura por Plugin**: Cada plugin vive en su propio subdirectorio con nombre en `kebab-case` (ejemplo: `noise-gate/`, `compressor/`, `parametric-eq/`).
- **Nomenclatura**:
  - Código FAUST principal: `<plugin_name>.dsp` en `snake_case` (ejemplo: `noise_gate.dsp`).
  - Identificador de compilación: `NAME = <plugin_name>` (ejemplo: `NAME = noise_gate`).
- **Makefile Unificado**: El `Makefile` de cada plugin NO debe duplicar lógica de construcción ni rutas. Debe limitarse a:
  ```makefile
  DSP  = <plugin_name>.dsp
  NAME = <plugin_name>

  include ../scripts/plugin_common.mk
  ```
- **Recursos Compartidos**:
  - `daw-plugins/JUCE/`: Instalación compartida de JUCE 9 (módulos y `Projucer.app`).
  - `daw-plugins/scripts/patch_juce_gui.py`: Script centralizado de parcheo de compatibilidad JUCE 9, macOS 13.0+ y tema oscuro Ableton Live.
  - `daw-plugins/scripts/plugin_common.mk`: Reglas comunes de `make` (`check`, `juce`, `build`, `build-au`, `build-standalone`, `svg`, `clean`).

---

## 2. Estándar de Procesamiento de Señal (FAUST DSP)

1. **Metadatos Declarativos Obligatorios**:
   Todo archivo `.dsp` debe iniciar con:
   ```faust
   declare name        "<PluginName>";
   declare version     "1.0.0";
   declare author      "<Author>";
   declare license     "MIT";
   declare description "<Descripción concisa del procesador>";

   import("stdfaust.lib");
   ```
2. **Prevención de Clicks y Zipper Noise**:
   - Todo parámetro de control continuo (`Threshold`, `Gain`, `Frequency`, `Floor`, etc.) debe suavizarse mediante `: si.smoo` o filtros paso bajo de control apropiados.
   - Envolventes de ganancia o compresión deben ser $C^1$ continuas (usar `an.amp_follower_ar`, generadores acústicos continuos o suavizadores de corte).
3. **Coherencia Estéreo**:
   - Para plugins de dinámica (gates, compresores, limitadores), la detección debe ser vinculada estéreo (ejemplo: `sqrt(0.5 * (l*l + r*r))`) para preservar la imagen estéreo sin desfases entre canales.
4. **Preservación de Parámetros**:
   - Al modificar o refactorizar un plugin existente, **NUNCA cambies o renombres los identificadores de parámetros** ya expuestos para no romper sesiones de usuario ni automatizaciones guardadas en DAWs.

---

## 3. Estándar de Interfaz Gráfica (UI/UX Inspirado en Ableton Live)

La interfaz gráfica por defecto generada por `faust2juce` es una torre vertical excesivamente grande y con bajo contraste. El estándar de este repositorio la transforma en un dispositivo horizontal compacto idéntico a los dispositivos nativos de **Ableton Live**:

1. **Layout Horizontal Obligatorio**:
   - **PROHIBIDO** usar `vgroup` como contenedor principal o crear diseños verticales altos.
   - Todo plugin debe estructurarse en una barra horizontal mediante `hgroup`:
     ```faust
     plugin_group(x) = hgroup("[0] Plugin Name", x);
     params_group(x) = plugin_group(hgroup("[1] Parameters", x));
     meters_group(x) = plugin_group(hgroup("[2] Meters", x));
     ```
   - Dimensiones objetivo de ventana: **ancho de 380–520 px**, **altura de 170–210 px**.
2. **Controles Rotativos y Medidores**:
   - Sliders de parámetros numéricos deben declararse como perillas rotativas: `[style:knob]`.
   - Incluir siempre unidad (`[unit:dB]`, `[unit:ms]`, `[unit:Hz]`, etc.), rango numérico y escala logarítmica si aplica (`[scale:log]`).
   - Medidores visuales deben ubicarse en el grupo lateral derecho usando `vbargraph` para barras verticales compactas.
3. **Paleta y Tipografía (`AbletonDarkLookAndFeel`)**:
   - **Fondo de ventana**: Carbón mate `#18191C`.
   - **Paneles y tarjetas**: `#22242A` con borde redondeado (4px) y contorno sutil `#32353E`.
   - **Títulos de sección / grupos**: `#8A8E99` (gris medio claro, 10 pt bold en mayúsculas).
   - **Etiquetas de parámetros**: `#E0E3EB` (plata brillante de alto contraste, 11 pt bold).
   - **Valores numéricos y arcos activos**: Cyan Ableton `#00D2FF` (10 pt bold).
   - **Prohibido**: Cero texto negro sobre fondo oscuro. Ningún widget puede renderizarse con `juce::Colours::black` sobre fondos oscuros.

---

## 4. Flujo de Compilación y Automatización

Para cualquier plugin, el flujo de desarrollo y compilación sigue los mismos comandos en consola:

1. **Validación de Sintaxis**:
   ```bash
   make check
   ```
   Valida el archivo `.dsp` y comprueba la generación de código C++ limpio sin warnings de sintaxis.

2. **Generación JUCE + Parcheo Automático**:
   ```bash
   make juce
   ```
   Ejecuta `faust2juce`, aplica `scripts/patch_juce_gui.py` (inyectando compatibilidad macOS 13.0, API de fuentes JUCE 9 y `AbletonDarkLookAndFeel`), y regenera el proyecto Xcode con `Projucer --resave --fix-missing-dependencies`.

3. **Compilación de Binarios VST3 / AU / Standalone**:
   ```bash
   make build            # Compila VST3 e instala en ~/Library/Audio/Plug-Ins/VST3/
   make build-au         # Compila Audio Unit e instala en ~/Library/Audio/Plug-Ins/Components/
   make build-standalone # Compila versión ejecutable independiente para pruebas
   ```

---

## 5. Verificación Obligatoria Antes de Entregar Cambios

Antes de dar por completado cualquier plugin nuevo o cambio en uno existente:
1. Ejecutar `make check` y validar que no existan errores ni advertencias en Faust.
2. Si se modificó la lógica DSP, escribir o ejecutar una verificación matemática en C++ o test de respuesta de señal (por ejemplo, comprobar respuesta a impulsos, umbrales o suavizado).
3. Ejecutar `make juce` y luego `make build` y `make build-au`.
4. Verificar que `git status` no muestre archivos generados o binarios no deseados.
5. Recordar al usuario la recarga en Ableton Live 12 Lite con `Option` (⌥) + clic en **Rescan Plugins**.
