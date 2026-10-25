---
name: faust-juce-plugin
description: >-
  Standardized guide and workflow for creating, modifying, styling, and compiling
  audio plugins in the daw-plugins repository using FAUST, JUCE 9, and Xcode on macOS.
---

# Faust JUCE Plugin Skill

Use this skill whenever you are asked to create a new audio plugin or modify/refactor an existing plugin in this repository. It guarantees full alignment with the repository standard established by the Noise Gate plugin.

---

## 1. Quick Checklist for Creating a New Plugin

When creating a new plugin (e.g. `compressor/`):

1. **Create the Plugin Directory**:
   ```bash
   mkdir -p compressor
   ```
2. **Create the `Makefile`**:
   The `Makefile` must only contain:
   ```makefile
   DSP  = compressor.dsp
   NAME = compressor

   include ../scripts/plugin_common.mk
   ```
3. **Write the `.dsp` File**:
   - Follow the horizontal layout with `hgroup` (prohibit vertical stacking).
   - Use `[style:knob]` for rotaries and `vbargraph` for meters.
   - Smooth all parameters with `si.smoo`.
   - Prevent clicks with continuous envelopes.
4. **Compile and Verify**:
   ```bash
   cd compressor
   make check
   make juce
   make build
   make build-au
   make build-standalone
   ```

---

## 2. DSP Template Reference

```faust
declare name        "MyPlugin";
declare version     "1.0.0";
declare author      "Franco Moloche";
declare license     "MIT";
declare description "Concise description of the plugin";

import("stdfaust.lib");

// Horizontal groups: Ableton Live Device layout
plugin_group(x) = hgroup("[0] My Plugin", x);
params_group(x) = plugin_group(hgroup("[1] Parameters", x));
meters_group(x) = plugin_group(hgroup("[2] Meters", x));

// Parameters (Knobs)
gain_db = params_group(hslider("[0] Gain [unit:dB][style:knob][tooltip: Gain in dB]", 0.0, -40.0, 20.0, 0.1)) : si.smoo;
speed   = params_group(hslider("[1] Speed [unit:ms][style:knob][scale:log][tooltip: Speed in ms]", 10.0, 1.0, 500.0, 1.0));

// Meters (Vertical bars)
meter_out(x) = attach(x, max(ba.db2linear(-80.0), x) : ba.linear2db : meters_group(vbargraph("[0] Out [unit:dB]", -80.0, 0.0)));

// Processing
process(l, r) = l * g : meter_out, r * g : meter_out
with {
    g = ba.db2linear(gain_db);
};
```

---

## 3. UI and Styling Details

All styling is automated by `scripts/patch_juce_gui.py`:
- Window size: Horizontal compact (~450 × 196 px).
- Palette:
  - Background: `#18191C` (Dark charcoal)
  - Cards: `#22242A` (Border `#32353E`)
  - Headings: `#8A8E99` (10 pt bold uppercase)
  - Labels: `#E0E3EB` (11 pt bold)
  - Values / Arcs: `#00D2FF` (Ableton Cyan)
- No manual C++ GUI editing is required; running `make juce` patches the generated C++ files automatically.

---

## 4. Verification Workflow

1. **Faust syntax check**: `make check`
2. **DSP validation**: Write and run a C++ test script if new dynamic/filter math was introduced.
3. **JUCE project update**: `make juce`
4. **Compile targets**:
   - `make build` (VST3 -> `~/Library/Audio/Plug-Ins/VST3/`)
   - `make build-au` (AU -> `~/Library/Audio/Plug-Ins/Components/`)
   - `make build-standalone` (Standalone app -> check window geometry)
5. **DAW Rescan**: Guide the user to press `Option` (⌥) + click **Rescan Plugins** in Ableton Live.
