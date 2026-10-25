declare name        "FeedbackSuppressor";
declare version     "1.0.0";
declare author      "Franco Moloche";
declare license     "MIT";
declare description "Automatic Surgical Feedback Suppressor with Room Calibration and Suppression Visualizer";

import("stdfaust.lib");

// ============================================================================
// UI Groups & Controls (Ableton Live Compact Horizontal Layout)
// ============================================================================
plugin_group(x) = hgroup("[0] Feedback Suppressor", x);
params_group(x) = plugin_group(hgroup("[1] Controls", x));
meters_group(x) = plugin_group(hgroup("[2] Suppression Visualizer", x));

// Calibration and Reset triggers
calibrate      = params_group(checkbox("[0] Calibrate [tooltip: Quick scan room acoustic resonances and lock notch filters]"));
reset          = params_group(button("[1] Reset [tooltip: Clear room calibration memory]"));

// Core analytical parameters
sensitivity_db = params_group(hslider("[2] Sensitivity [unit:dB][style:knob][tooltip: Feedback detection sensitivity threshold]", -30.0, -60.0, -6.0, 0.5)) : si.smoo;
max_cut_db     = params_group(hslider("[3] Max Cut [unit:dB][style:knob][tooltip: Maximum notch attenuation depth]", -24.0, -48.0, 0.0, 0.5)) : si.smoo;
sharpness_q    = params_group(hslider("[4] Sharpness [style:knob][tooltip: Surgical notch filter quality factor Q]", 35.0, 10.0, 60.0, 1.0)) : si.smoo;
gain_db        = params_group(hslider("[5] Gain [unit:dB][style:knob][tooltip: Clean output trim gain in dB]", 0.0, -12.0, 18.0, 0.1)) : si.smoo;

// Input RMS visual meter
meter_in(x)    = attach(x, max(ba.db2linear(-60.0), x) : ba.linear2db : meters_group(vbargraph("[8] In [unit:dB]", -60.0, 0.0)));

// ============================================================================
// DSP Detection & Surgical Notch Filtering
// ============================================================================

// Stereo detection input
stereo_mono(l, r) = 0.5 * (l + r);
stereo_rms(l, r)  = sqrt(max(0.0, 0.5 * (l * l + r * r))) : an.rms_envelope_tau(0.010);

thresh_lin = ba.db2linear(sensitivity_db);

// Asymmetric smoother for fast millisecond attack (1.5 ms) and transparent decay (350 ms)
smooth_cut(target) = loop ~ _
with {
    att_coeff = 1.0 - exp(-1.0 / max(1.0, 0.0015 * ma.SR));
    rel_coeff = 1.0 - exp(-1.0 / max(1.0, 0.3500 * ma.SR));
    loop(y) = ba.if(reset > 0.5, 0.0, ba.if(target < y, y + att_coeff * (target - y), y + rel_coeff * (target - y)));
};

// Room calibration peak-hold latch: captures and locks notch cuts while calibrate is active
latch_room_cut(dyn) = loop ~ _
with {
    loop(fb) = ba.if(reset > 0.5, 0.0, ba.if(calibrate > 0.5, min(dyn, fb), fb));
};

// Analytical Band Processor: detects tonal resonance and computes surgical cut in dB
process_band_detector(fc, mono_sig) = effective_cut_db
with {
    q_narrow = max(8.0, sharpness_q * 0.75);
    q_wide   = 1.8;
    // Peak gain normalized to 1.0 (gain = 1/Q)
    s_narrow = mono_sig : fi.resonbp(fc, q_narrow, 1.0 / q_narrow);
    s_wide   = mono_sig : fi.resonbp(fc, q_wide, 1.0 / q_wide);

    env_narrow = s_narrow : an.amp_follower_ar(0.0015, 0.120);
    env_wide   = s_wide   : an.amp_follower_ar(0.0100, 0.250);

    // Feedback is an intense tonal resonance: high narrow energy concentrating most neighborhood power
    is_feedback = (env_narrow > thresh_lin) & (env_narrow > env_wide * 0.75);
    excess_db   = ba.linear2db(env_narrow / max(ba.db2linear(-90.0), thresh_lin));

    target_cut  = ba.if(is_feedback, max_cut_db * min(1.0, max(0.2, excess_db / 18.0)), 0.0);
    dyn_cut_db  = smooth_cut(target_cut);

    room_cut_db = latch_room_cut(dyn_cut_db);
    total_cut   = min(dyn_cut_db, room_cut_db);
    effective_cut_db = max(max_cut_db, total_cut);
};

// Surgical Notch Filter Section for stereo pair (l, r)
apply_notch(fc, cut_db) = fi.peak_eq_cq(cut_db, fc, sharpness_q),
                          fi.peak_eq_cq(cut_db, fc, sharpness_q);

// 8 Critical Feedback Frequencies
fc0 = 160.0;
fc1 = 315.0;
fc2 = 630.0;
fc3 = 1250.0;
fc4 = 2200.0;
fc5 = 3800.0;
fc6 = 6300.0;
fc7 = 10000.0;

// Band Meters displaying actual dB of cut applied ([-48, 0] dB)
meter_band0(cut) = attach(cut, cut : meters_group(vbargraph("[0] 160Hz [unit:dB]", -48.0, 0.0)));
meter_band1(cut) = attach(cut, cut : meters_group(vbargraph("[1] 315Hz [unit:dB]", -48.0, 0.0)));
meter_band2(cut) = attach(cut, cut : meters_group(vbargraph("[2] 630Hz [unit:dB]", -48.0, 0.0)));
meter_band3(cut) = attach(cut, cut : meters_group(vbargraph("[3] 1.2k [unit:dB]", -48.0, 0.0)));
meter_band4(cut) = attach(cut, cut : meters_group(vbargraph("[4] 2.2k [unit:dB]", -48.0, 0.0)));
meter_band5(cut) = attach(cut, cut : meters_group(vbargraph("[5] 3.8k [unit:dB]", -48.0, 0.0)));
meter_band6(cut) = attach(cut, cut : meters_group(vbargraph("[6] 6.3k [unit:dB]", -48.0, 0.0)));
meter_band7(cut) = attach(cut, cut : meters_group(vbargraph("[7] 10k [unit:dB]", -48.0, 0.0)));

// ============================================================================
// Main Process
// ============================================================================
process(l, r) = (l, r)
              : apply_notch(fc0, cut0)
              : apply_notch(fc1, cut1)
              : apply_notch(fc2, cut2)
              : apply_notch(fc3, cut3)
              : apply_notch(fc4, cut4)
              : apply_notch(fc5, cut5)
              : apply_notch(fc6, cut6)
              : apply_notch(fc7, cut7)
              : (*(out_gain) : attach_rms), *(out_gain)
with {
    mono_sig = stereo_mono(l, r);
    rms_val  = stereo_rms(l, r) : meter_in;
    attach_rms(x) = attach(x, rms_val);

    // Detect and measure cuts for each frequency band
    cut0 = process_band_detector(fc0, mono_sig) : meter_band0;
    cut1 = process_band_detector(fc1, mono_sig) : meter_band1;
    cut2 = process_band_detector(fc2, mono_sig) : meter_band2;
    cut3 = process_band_detector(fc3, mono_sig) : meter_band3;
    cut4 = process_band_detector(fc4, mono_sig) : meter_band4;
    cut5 = process_band_detector(fc5, mono_sig) : meter_band5;
    cut6 = process_band_detector(fc6, mono_sig) : meter_band6;
    cut7 = process_band_detector(fc7, mono_sig) : meter_band7;

    out_gain = ba.db2linear(gain_db);
};
