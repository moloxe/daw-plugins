#!/usr/bin/env python3
"""
Patch script for Faust JUCE plugins to provide an Ableton-inspired,
compact dark theme with high-contrast typography and sleek controls.
"""

import sys
import os
import re

def patch_jucer(jucer_path):
    if not os.path.exists(jucer_path):
        print(f"Warning: {jucer_path} not found.")
        return
    with open(jucer_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Add osxCompatibility="13.0 SDK" if not present
    if 'osxCompatibility=' not in content:
        content = re.sub(
            r'targetName="([^"]+)"\s*/>',
            r'targetName="\1" osxCompatibility="13.0 SDK"/>',
            content
        )
        with open(jucer_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✓ Patched {jucer_path} for macOS 13.0 SDK compatibility.")

ABLETON_LOOK_AND_FEEL = """
// ==============================================================================
// AbletonDarkLookAndFeel - Modern compact dark UI for DAW plugins
// ==============================================================================
struct AbletonDarkLookAndFeel : public juce::LookAndFeel_V4
{
    AbletonDarkLookAndFeel()
    {
        setColour (juce::ResizableWindow::backgroundColourId, juce::Colour (0xff18191c));
        setColour (juce::Slider::backgroundColourId, juce::Colour (0xff18191c));
        setColour (juce::Slider::rotarySliderFillColourId, juce::Colour (0xff00d2ff)); // Ableton Cyan
        setColour (juce::Slider::rotarySliderOutlineColourId, juce::Colour (0xff2d3038)); // Track
        setColour (juce::Slider::thumbColourId, juce::Colours::white);
        setColour (juce::Slider::textBoxTextColourId, juce::Colour (0xff00d2ff)); // Cyan value
        setColour (juce::Slider::textBoxBackgroundColourId, juce::Colour (0xff141518));
        setColour (juce::Slider::textBoxOutlineColourId, juce::Colours::transparentBlack);
        setColour (juce::Slider::textBoxHighlightColourId, juce::Colour (0x4000d2ff));
        setColour (juce::Label::textColourId, juce::Colour (0xffe0e3eb));
        setColour (juce::TextButton::buttonColourId, juce::Colour (0xff25272d));
        setColour (juce::TextButton::buttonOnColourId, juce::Colour (0xff00d2ff));
        setColour (juce::TextButton::textColourOffId, juce::Colour (0xffd0d4dd));
        setColour (juce::TextButton::textColourOnId, juce::Colours::black);
    }

    juce::Font getLabelFont (juce::Label&) override
    {
        return juce::Font (juce::FontOptions (10.0f, juce::Font::bold));
    }

    void drawRotarySlider (juce::Graphics& g, int x, int y, int width, int height,
                           float sliderPos, float rotaryStartAngle, float rotaryEndAngle,
                           juce::Slider& slider) override
    {
        const float minDim = (float) juce::jmin (width, height);
        const float radius = minDim * 0.5f - 3.0f;
        const float centreX = (float) x + (float) width * 0.5f;
        const float centreY = (float) y + (float) height * 0.5f;
        const float rx = centreX - radius;
        const float ry = centreY - radius;
        const float rw = radius * 2.0f;
        const float angle = rotaryStartAngle + sliderPos * (rotaryEndAngle - rotaryStartAngle);
        const bool isMouseOver = slider.isMouseOverOrDragging() && slider.isEnabled();

        // 1. Dial base / background circle
        g.setColour (juce::Colour (0xff23252b));
        g.fillEllipse (rx, ry, rw, rw);
        g.setColour (juce::Colour (0xff32353e));
        g.drawEllipse (rx, ry, rw, rw, 1.0f);

        // 2. Track background arc
        const float trackThickness = 3.2f;
        juce::Path trackPath;
        trackPath.addCentredArc (centreX, centreY, radius - trackThickness * 0.5f, radius - trackThickness * 0.5f,
                                 0.0f, rotaryStartAngle, rotaryEndAngle, true);
        g.setColour (juce::Colour (0xff2d3038));
        g.strokePath (trackPath, juce::PathStrokeType (trackThickness, juce::PathStrokeType::curved, juce::PathStrokeType::rounded));

        // 3. Active value arc (Ableton Cyan)
        if (slider.isEnabled() && std::abs (angle - rotaryStartAngle) > 0.001f)
        {
            juce::Path valPath;
            valPath.addCentredArc (centreX, centreY, radius - trackThickness * 0.5f, radius - trackThickness * 0.5f,
                                   0.0f, rotaryStartAngle, angle, true);
            g.setColour (isMouseOver ? juce::Colour (0xff3ae5ff) : juce::Colour (0xff00d2ff));
            g.strokePath (valPath, juce::PathStrokeType (trackThickness, juce::PathStrokeType::curved, juce::PathStrokeType::rounded));
        }

        // 4. Center inner dial cap
        const float innerRadius = radius * 0.65f;
        g.setColour (juce::Colour (0xff18191c));
        g.fillEllipse (centreX - innerRadius, centreY - innerRadius, innerRadius * 2.0f, innerRadius * 2.0f);

        // 5. White pointer needle
        juce::Path needle;
        needle.startNewSubPath (centreX + std::sin (angle) * (radius * 0.22f),
                                centreY - std::cos (angle) * (radius * 0.22f));
        needle.lineTo (centreX + std::sin (angle) * (radius * 0.85f),
                       centreY - std::cos (angle) * (radius * 0.85f));
        g.setColour (slider.isEnabled() ? juce::Colours::white : juce::Colour (0xff707580));
        g.strokePath (needle, juce::PathStrokeType (2.0f, juce::PathStrokeType::curved, juce::PathStrokeType::rounded));
    }
};
"""

NEW_UI_BOX_PAINT = """        void paint(juce::Graphics& g) override
        {
            auto b = getLocalBounds().toFloat().reduced(1.0f);
            g.setColour(juce::Colour(0xff22242a));
            g.fillRoundedRectangle(b, 4.0f);
            g.setColour(juce::Colour(0xff32353e));
            g.drawRoundedRectangle(b, 4.0f, 1.0f);

            if (isNameDisplayed()) {
                g.setFont(juce::Font(juce::FontOptions(10.0f, juce::Font::bold)));
                g.setColour(juce::Colour(0xff8a8e99));
                g.drawText(getName().toUpperCase(), getLocalBounds().withHeight(kNameHeight + 4), juce::Justification::centred);
            }
        }"""

NEW_UI_SLIDER_PAINT = """        virtual void paint(juce::Graphics& g) override
        {
            if (fType == VSlider || fType == Knob) {
                g.setFont(juce::Font(juce::FontOptions(11.0f, juce::Font::bold)));
                g.setColour(juce::Colour(0xffe0e3eb));
                g.drawText(getName(), getLocalBounds().withHeight(kNameHeight), juce::Justification::centredTop);
            }
        }"""

NEW_UI_VUMETER_DRAW = """        void drawVBargraph(juce::Graphics& g, int width, int height)
        {
            float x = (float)(getWidth()-width)/2;
            float y;
            if (isNameDisplayed()) {
                y = 18.0f;
                height = getHeight() - 38;
                // VUMeter Name
                g.setFont(juce::Font(juce::FontOptions(10.5f, juce::Font::bold)));
                g.setColour(juce::Colour(0xffe0e3eb));
                g.drawText(getName(), getLocalBounds().withHeight(16), juce::Justification::centredTop);
            } else {
                y = 4.0f;
                height = getHeight() - 24;
            }
            
            // VUMeter Outline & Background
            g.setColour(juce::Colour(0xff33363f));
            g.drawRect(x, y, (float)width, (float)height, 1.0f);
            g.setColour(juce::Colour(0xff121316));
            g.fillRect(x+1.0f, y+1.0f, (float)width-2.0f, (float)height-2.0f);
            
            // Modern dark pill readout
            auto pill = juce::Rectangle<float>(juce::jmax((getWidth()-44)/2, 0), (float)(getHeight()-18), (float)juce::jmin(getWidth(), 44), 16.0f);
            g.setColour(juce::Colour(0xff141518));
            g.fillRoundedRectangle(pill, 3.0f);
            g.setColour(juce::Colour(0xff2d3038));
            g.drawRoundedRectangle(pill, 3.0f, 0.8f);
            
            fDB ? drawVBargraphDB (g, x, width) : drawVBargraphLin(g, x, width);
        }"""

NEW_UI_VUMETER_SETUP_LABEL = """        void setupLabel(juce::String tooltip)
        {
            setLabelPos();
            fLabel.setEditable(false, false, false);
            fLabel.setJustificationType(juce::Justification::centred);
            fLabel.setFont(juce::Font(juce::FontOptions(9.0f, juce::Font::bold)));
            fLabel.setColour(juce::Label::textColourId, juce::Colour(0xff00d2ff));
            fLabel.setText(juce::String(*fZone) + " " + fUnit, juce::dontSendNotification);
            fLabel.setTooltip(tooltip);
            addAndMakeVisible(fLabel);
        }"""

def patch_processor(processor_path):
    if not os.path.exists(processor_path):
        print(f"Error: {processor_path} not found.")
        sys.exit(1)

    with open(processor_path, "r", encoding="utf-8") as f:
        src = f.read()

    # 1. JUCE 9 Font string width API
    src = src.replace(
        "juce::Font().getStringWidth(",
        "juce::GlyphArrangement::getStringWidthInt(juce::Font(juce::FontOptions()), "
    )

    # 2. Dimensions: Compact Ableton style
    src = re.sub(r'#define kKnobWidth \d+', '#define kKnobWidth 64', src)
    src = re.sub(r'#define kKnobHeight \d+', '#define kKnobHeight 68', src)
    src = re.sub(r'#define kVBargraphWidth \d+', '#define kVBargraphWidth 36', src)
    src = re.sub(r'#define kVBargraphHeight \d+', '#define kVBargraphHeight 96', src)
    src = re.sub(r'#define kMargin \d+', '#define kMargin 6', src)
    src = re.sub(r'#define kNameHeight \d+', '#define kNameHeight 15', src)

    # 3. Knob text box dimensions
    src = src.replace(
        'fSlider.setTextBoxStyle(juce::Slider::TextBoxBelow, false, 60, 20);',
        'fSlider.setTextBoxStyle(juce::Slider::TextBoxBelow, false, 52, 16);'
    )

    # 4. Inject AbletonDarkLookAndFeel instead of unused CustomLookAndFeel
    # Locate struct CustomLookAndFeel
    custom_laf_pattern = r'struct CustomLookAndFeel\s*:\s*public juce::LookAndFeel_V3\s*\{.*?\n\};'
    if re.search(custom_laf_pattern, src, re.DOTALL):
        src = re.sub(custom_laf_pattern, ABLETON_LOOK_AND_FEEL.strip(), src, flags=re.DOTALL)
    else:
        # Fallback: prepend before enum SliderType
        src = src.replace('enum SliderType {', ABLETON_LOOK_AND_FEEL.strip() + '\n\nenum SliderType {')

    # Use AbletonDarkLookAndFeel in JuceGUI
    src = src.replace(
        'std::unique_ptr<juce::LookAndFeel> fLaf = std::make_unique<juce::LookAndFeel_V4>();',
        'std::unique_ptr<juce::LookAndFeel> fLaf = std::make_unique<AbletonDarkLookAndFeel>();'
    )

    # 5. Patch uiBox::paint
    old_box_paint_pattern = r'void paint\(juce::Graphics& g\) override\s*\{\s*// Fill the box background in gray shades.*?g\.drawText\(getName\(\), getLocalBounds\(\)\.withHeight\(kNameHeight\), juce::Justification::centred\);\s*\}\s*\}'
    if re.search(old_box_paint_pattern, src, re.DOTALL):
        src = re.sub(old_box_paint_pattern, NEW_UI_BOX_PAINT, src, flags=re.DOTALL)
    else:
        print("Note: uiBox::paint pattern not matched directly, attempting targeted replacement.")
        src = src.replace(
            "g.setColour(juce::Colours::black.withAlpha(0.5f));",
            "g.setColour(juce::Colour(0xff22242a));"
        )

    # 6. Patch uiSlider::paint
    old_slider_paint = """        virtual void paint(juce::Graphics& g) override
        {
            if (fType == VSlider || fType == Knob) {
                g.setColour(juce::Colours::black);
                g.drawText(getName(), getLocalBounds(), juce::Justification::centredTop);
            }
        }"""
    src = src.replace(old_slider_paint, NEW_UI_SLIDER_PAINT)

    # 7. Patch uiVUMeter::drawVBargraph
    old_vumeter_draw_pattern = r'void drawVBargraph\(juce::Graphics& g, int width, int height\)\s*\{.*?fDB \? drawVBargraphDB \(g, x, width\) : drawVBargraphLin\(g, x, width\);\s*\}'
    if re.search(old_vumeter_draw_pattern, src, re.DOTALL):
        src = re.sub(old_vumeter_draw_pattern, NEW_UI_VUMETER_DRAW, src, flags=re.DOTALL)

    # 8. Patch uiVUMeter::setupLabel and setLabelPos
    src = src.replace(
        'fLabel.setBounds((getWidth()-50)/2, getHeight()-22, 50, 20);',
        'fLabel.setBounds((getWidth()-44)/2, getHeight()-18, 44, 16);'
    )

    old_setup_label = """        void setupLabel(juce::String tooltip)
        {
            setLabelPos();
            fLabel.setEditable(false, false, false);
            fLabel.setJustificationType(juce::Justification::centred);
            fLabel.setText(juce::String(*fZone) + " " + fUnit, juce::dontSendNotification);
            fLabel.setTooltip(tooltip);
            addAndMakeVisible(fLabel);
        }"""
    src = src.replace(old_setup_label, NEW_UI_VUMETER_SETUP_LABEL)

    # 9. Meter scale text color and size in drawVBargraphDB
    src = src.replace(
        "g.setFont(9.0f);\n            g.setColour(juce::Colours::white);",
        "g.setFont(juce::Font(juce::FontOptions(8.0f)));\n            g.setColour(juce::Colour(0xff8a8e99));"
    )

    # 10. Editor window background: dark background instead of white
    old_editor_paint = """void FaustPlugInAudioProcessorEditor::paint (juce::Graphics& g)
{
    g.fillAll (juce::Colours::white);
}"""
    new_editor_paint = """void FaustPlugInAudioProcessorEditor::paint (juce::Graphics& g)
{
    g.fillAll (juce::Colour(0xff18191c));
}"""
    src = src.replace(old_editor_paint, new_editor_paint)

    with open(processor_path, "w", encoding="utf-8") as f:
        f.write(src)
    print(f"✓ Patched {processor_path} with Ableton Dark Theme & compact geometry.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: patch_juce_gui.py <project_name>")
        sys.exit(1)
    name = sys.argv[1]
    jucer_file = os.path.join(name, f"{name}.jucer")
    processor_file = os.path.join(name, "FaustPluginProcessor.cpp")
    patch_jucer(jucer_file)
    patch_processor(processor_file)
