declare name        "NoiseGate";
declare version     "1.0.0";
declare author      "Franco Moloche";
declare license     "MIT";
declare description "Stereo RMS Noise Gate with Threshold, Attack, Hold, Release, and Floor controls";

import("stdfaust.lib");

// ============================================================================
// UI Controls (Grouped for Faust IDE, faust2juce and DAW hosts)
// ============================================================================
gate_group(x)   = vgroup("[0] Stereo Noise Gate", x);
params_group(x) = gate_group(vgroup("[1] Parameters", x));
meters_group(x) = gate_group(hgroup("[2] Meters", x));

// Threshold (dB): Level above which the gate opens
threshold_db = params_group(hslider("[0] Threshold [unit:dB][style:knob][tooltip: Threshold level in dB]", -40.0, -80.0, 0.0, 0.1)) : si.smoo;

// Attack (ms): Time taken for the gate to fully open once triggered
attack_ms    = params_group(hslider("[1] Attack [unit:ms][style:knob][scale:log][tooltip: Attack time in milliseconds]", 5.0, 0.1, 200.0, 0.1));

// Hold (ms): Time the gate stays open after signal falls below threshold
hold_ms      = params_group(hslider("[2] Hold [unit:ms][style:knob][tooltip: Hold time in milliseconds]", 50.0, 0.0, 1000.0, 1.0));

// Release (ms): Time taken for the gate to close down to floor gain
release_ms   = params_group(hslider("[3] Release [unit:ms][style:knob][scale:log][tooltip: Release time in milliseconds]", 150.0, 1.0, 2000.0, 1.0));

// Floor (dB): Gain attenuation when the gate is closed (prevents harsh silence)
floor_db     = params_group(hslider("[4] Floor [unit:dB][style:knob][tooltip: Minimum gain level when gate is closed]", -60.0, -80.0, 0.0, 0.1)) : si.smoo;

// ============================================================================
// DSP Processing
// ============================================================================

// 1. Stereo-linked RMS envelope detector (~10 ms integration window)
rms_tau_sec      = 0.010;
stereo_in(l, r)  = sqrt(max(0.0, 0.5 * (l * l + r * r)));
stereo_rms(l, r) = stereo_in(l, r) : an.rms_envelope_tau(rms_tau_sec);

// 2. Trigger comparator (1 when signal >= threshold, 0 otherwise)
thresh_lin = ba.db2linear(threshold_db);
raw_trig(env) = env >= thresh_lin;

// 3. Sample-accurate Hold stage
// When trigger drops to 0, hold_stage keeps output high for hold_samples.
hold_samples = int(max(0.0, hold_ms * 0.001 * ma.SR));
hold_stage(trig) = (trig > 0) | (countdown(trig) > 0)
with {
    countdown(t) = ba.if(t > 0, hold_samples, max(0, _ - 1)) ~ _;
};

// 4. Click-free Attack / Release smoother
// Standard acoustic definitions:
// Attack time: time to reach 99% open (-40 dB to 0 dB, ~4.6 * tau)
// Release time: time to decay 60 dB (t60, ln(1000) * tau ~ 6.908 * tau)
attack_tau  = max(0.00005, (attack_ms * 0.001) / 4.60517);
release_tau = max(0.0001,  (release_ms * 0.001) / 6.907755);
gate_env    = an.amp_follower_ar(attack_tau, release_tau);

// 5. Floor gain mapping
floor_lin   = ba.db2linear(floor_db);

// Visual meters for Faust IDE and JUCE GUI
meter_env(x) = attach(x, max(ba.db2linear(-80.0), x) : ba.linear2db : meters_group(vbargraph("[0] Input RMS [unit:dB]", -80.0, 0.0)));
meter_gain(g) = attach(g, max(ba.db2linear(-80.0), g) : ba.linear2db : meters_group(vbargraph("[1] Gate Gain [unit:dB]", -80.0, 0.0)));

// Compute continuous gain envelope [floor_lin .. 1.0]
compute_gain(l, r) = stereo_rms(l, r)
                   : meter_env
                   : raw_trig
                   : hold_stage
                   : gate_env
                   : *(1.0 - floor_lin) + floor_lin
                   : meter_gain;

// ============================================================================
// Main Stereo Process
// ============================================================================
process(l, r) = l * g, r * g
with {
    g = compute_gain(l, r);
};
