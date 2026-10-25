#!/usr/bin/env python3
"""
Patch script for Faust JUCE plugins to provide an Ableton-inspired,
compact dark theme with high-contrast typography and sleek controls.
Applicable across all plugins in the daw-plugins repository.
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
        
        // Buttons
        setColour (juce::TextButton::buttonColourId, juce::Colour (0xff25272d));
        setColour (juce::TextButton::buttonOnColourId, juce::Colour (0xff00d2ff));
        setColour (juce::TextButton::textColourOffId, juce::Colour (0xffd0d4dd));
        setColour (juce::TextButton::textColourOnId, juce::Colours::black);
        
        // Toggle & Checkbuttons
        setColour (juce::ToggleButton::textColourId, juce::Colour (0xffe0e3eb));
        setColour (juce::ToggleButton::tickColourId, juce::Colour (0xff00d2ff));
        setColour (juce::ToggleButton::tickDisabledColourId, juce::Colour (0xff50535e));
        
        // Dropdown menus / Combobox
        setColour (juce::ComboBox::backgroundColourId, juce::Colour (0xff22242a));
        setColour (juce::ComboBox::textColourId, juce::Colour (0xffe0e3eb));
        setColour (juce::ComboBox::outlineColourId, juce::Colour (0xff32353e));
        setColour (juce::ComboBox::arrowColourId, juce::Colour (0xff8a8e99));
        setColour (juce::PopupMenu::backgroundColourId, juce::Colour (0xff1c1d22));
        setColour (juce::PopupMenu::textColourId, juce::Colour (0xffe0e3eb));
        setColour (juce::PopupMenu::highlightedBackgroundColourId, juce::Colour (0xff00d2ff));
        setColour (juce::PopupMenu::highlightedTextColourId, juce::Colours::black);
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

NEW_UI_MENU_PAINT = """        virtual void paint(juce::Graphics& g) override
        {
            g.setFont(juce::Font(juce::FontOptions(10.5f, juce::Font::bold)));
            g.setColour(juce::Colour(0xffe0e3eb));
            g.drawText(getName(), getLocalBounds().withHeight(getHeight()/2), juce::Justification::centredTop);
        }"""

NEW_UI_RADIO_PAINT = """        virtual void paint(juce::Graphics& g) override
        {
            g.setFont(juce::Font(juce::FontOptions(10.5f, juce::Font::bold)));
            g.setColour(juce::Colour(0xffe0e3eb));
            g.drawText(getName(), getLocalBounds().withHeight(kNameHeight), juce::Justification::centredTop);
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

NEW_UI_HBARGRAPH_DRAW = """        void drawHBargraph(juce::Graphics& g, int width, int height)
        {
            float x;
            float y = (float)(getHeight()-height)/2;
            if (isNameDisplayed()) {
                x = 100;
                width -= x;
                // VUMeter Name
                g.setFont(juce::Font(juce::FontOptions(10.0f, juce::Font::bold)));
                g.setColour(juce::Colour(0xffe0e3eb));
                g.drawText(getName(), 0, y, 90, height, juce::Justification::centredRight);
            } else {
                x = 50;
                width -= x;
            }
            
            // VUMeter Background & Outline
            g.setColour(juce::Colour(0xff33363f));
            g.drawRect(x, y, (float)width, (float)height, 1.0f);
            g.setColour(juce::Colour(0xff121316));
            g.fillRect(x+1.0f, y+1.0f, (float)width-2.0f, (float)height-2.0f);
            
            // Dark readout pill
            auto pill = juce::Rectangle<float>((float)x - 48.0f, (float)(getHeight() - 18)/2.0f, 44.0f, 18.0f);
            g.setColour(juce::Colour(0xff141518));
            g.fillRoundedRectangle(pill, 3.0f);
            g.setColour(juce::Colour(0xff2d3038));
            g.drawRoundedRectangle(pill, 3.0f, 0.8f);
            
            fDB ? drawHBargraphDB (g, y, height) : drawHBargraphLin(g, x, y, width, height);
        }"""

NEW_UI_NUMDISPLAY_DRAW = """        void drawNumDisplay(juce::Graphics& g, int width, int height)
        {
            int x = (getWidth()-width) / 2;
            int y = (getHeight()-height) / 2;
            
            // Modern dark box
            g.setColour(juce::Colour(0xff141518));
            g.fillRoundedRectangle((float)x, (float)y, (float)width, (float)height, 3.0f);
            g.setColour(juce::Colour(0xff2d3038));
            g.drawRoundedRectangle((float)x, (float)y, (float)width, (float)height, 3.0f, 0.8f);
        }"""

NEW_UI_VUMETER_DRAW_DB = """        void drawVBargraphDB(juce::Graphics& g, int x, int width)
        {
            // Drawing Scale
            g.setFont(juce::Font(juce::FontOptions(8.0f)));
            g.setColour(juce::Colour(0xff8a8e99));
            for (int i = -10; i > fMin; i -= 10) {
                paintScale(g, i);
            }
            for (int i = -6; i < fMax; i += 3)  {
                paintScale(g, i);
            }

            // Check if this is a downward suppression / notch cut meter
            bool isCutMeter = (fMax == 0.0f && fMin >= -50.0f) || getName().contains("Cut") || getName().contains("Hz") || getName().endsWith("k");
            if (isCutMeter) {
                float yZero = (float) dB2y(0.0f);
                float yCut  = (float) dB2y(fLevel);
                if (yCut > yZero + 1.0f) {
                    // Modern Ableton Cyan gradient for surgical feedback suppression
                    juce::ColourGradient grad(juce::Colour(0xff00d2ff), (float)x, yZero,
                                              juce::Colour(0xff0088cc), (float)x, yCut, false);
                    g.setGradientFill(grad);
                    g.fillRect((float)x + 1.0f, yZero, (float)width - 2.0f, yCut - yZero);
                    // Needle highlight line at the cut floor
                    g.setColour(juce::Colour(0xffffffff));
                    g.drawHorizontalLine((int)yCut, (float)x + 1.0f, (float)x + (float)width - 1.0f);
                }
                return;
            }

            int alpha = 200;
            FAUSTFLOAT dblevel = dB2Scale(fLevel);

            // Drawing from the minimal range to the current level, or -10dB.
            g.setColour(juce::Colour((juce::uint8)40, (juce::uint8)160, (juce::uint8)40, (juce::uint8)alpha));
            g.fillRect(x+1.0f, juce::jmax(dB2y(fLevel), dB2y(-10)), (float)width-2, dB2y(fMin)-juce::jmax(dB2y(fLevel), dB2y(-10)));

            // Drawing from -10dB to the current level, or -6dB.
            if (dblevel > dB2Scale(-10)) {
                g.setColour(juce::Colour((juce::uint8)160, (juce::uint8)220, (juce::uint8)20, (juce::uint8)alpha));
                g.fillRect(x+1.0f, juce::jmax(dB2y(fLevel), dB2y(-6)), (float)width-2, dB2y(-10)-juce::jmax(dB2y(fLevel), dB2y(-6)));
            }
            // Drawing from -6dB to the current level, or -3dB.
            if (dblevel > dB2Scale(-6)) {
                g.setColour(juce::Colour((juce::uint8)220, (juce::uint8)220, (juce::uint8)20, (juce::uint8)alpha));
                g.fillRect(x+1.0f, juce::jmax(dB2y(fLevel), dB2y(-3)), (float)width-2, dB2y(-6)-juce::jmax(dB2y(fLevel), dB2y(-3)));
            }
            // Drawing from -3dB to the current level, or 0dB.
            if (dblevel > dB2Scale(-3)) {
                g.setColour(juce::Colour((juce::uint8)240, (juce::uint8)160, (juce::uint8)20, (juce::uint8)alpha));
                g.fillRect(x+1.0f, juce::jmax(dB2y(fLevel), dB2y(0)), (float)width-2, dB2y(-3)-juce::jmax(dB2y(fLevel), dB2y(0)));
            }
            // Drawing from 0dB to the current level, or the maximum range.
            if (dblevel > dB2Scale(0)) {
                g.setColour(juce::Colour((juce::uint8)240, (juce::uint8)0, (juce::uint8)20, (juce::uint8)alpha));
                g.fillRect(x+1.0f, juce::jmax(dB2y(fLevel), dB2y(fMax)), (float)width-2, dB2y(0)-juce::jmax(dB2y(fLevel), dB2y(fMax)));
            }
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

    # 2. Dimensions: Comprehensive compact geometry for all widgets
    dims = [
        (r'#define kKnobWidth \d+', '#define kKnobWidth 64'),
        (r'#define kKnobHeight \d+', '#define kKnobHeight 68'),
        (r'#define kVBargraphWidth \d+', '#define kVBargraphWidth 36'),
        (r'#define kVBargraphHeight \d+', '#define kVBargraphHeight 96'),
        (r'#define kHBargraphWidth \d+', '#define kHBargraphWidth 180'),
        (r'#define kHBargraphHeight \d+', '#define kHBargraphHeight 36'),
        (r'#define kVSliderWidth \d+', '#define kVSliderWidth 52'),
        (r'#define kVSliderHeight \d+', '#define kVSliderHeight 96'),
        (r'#define kHSliderWidth \d+', '#define kHSliderWidth 180'),
        (r'#define kHSliderHeight \d+', '#define kHSliderHeight 36'),
        (r'#define kButtonWidth \d+', '#define kButtonWidth 72'),
        (r'#define kButtonHeight \d+', '#define kButtonHeight 28'),
        (r'#define kCheckButtonWidth \d+', '#define kCheckButtonWidth 72'),
        (r'#define kCheckButtonHeight \d+', '#define kCheckButtonHeight 26'),
        (r'#define kMenuWidth \d+', '#define kMenuWidth 96'),
        (r'#define kMenuHeight \d+', '#define kMenuHeight 38'),
        (r'#define kRadioButtonWidth \d+', '#define kRadioButtonWidth 90'),
        (r'#define kRadioButtonHeight \d+', '#define kRadioButtonHeight 44'),
        (r'#define kNumEntryWidth \d+', '#define kNumEntryWidth 76'),
        (r'#define kNumEntryHeight \d+', '#define kNumEntryHeight 36'),
        (r'#define kNumDisplayWidth \d+', '#define kNumDisplayWidth 60'),
        (r'#define kNumDisplayHeight \d+', '#define kNumDisplayHeight 32'),
        (r'#define kMargin \d+', '#define kMargin 6'),
        (r'#define kNameHeight \d+', '#define kNameHeight 15')
    ]
    for pattern, repl in dims:
        src = re.sub(pattern, repl, src)

    # 3. Knob text box dimensions
    src = src.replace(
        'fSlider.setTextBoxStyle(juce::Slider::TextBoxBelow, false, 60, 20);',
        'fSlider.setTextBoxStyle(juce::Slider::TextBoxBelow, false, 52, 16);'
    )

    # 4. Inject AbletonDarkLookAndFeel
    custom_laf_pattern = r'struct CustomLookAndFeel\s*:\s*public juce::LookAndFeel_V3\s*\{.*?\n\};'
    if re.search(custom_laf_pattern, src, re.DOTALL):
        src = re.sub(custom_laf_pattern, ABLETON_LOOK_AND_FEEL.strip(), src, flags=re.DOTALL)
    elif 'struct AbletonDarkLookAndFeel' in src:
        # Update existing AbletonDarkLookAndFeel if present
        existing_ableton_pattern = r'struct AbletonDarkLookAndFeel\s*:\s*public juce::LookAndFeel_V4\s*\{.*?\n\};'
        src = re.sub(existing_ableton_pattern, ABLETON_LOOK_AND_FEEL.strip(), src, flags=re.DOTALL)
    else:
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

    # 7. Patch uiMenu::paint
    old_menu_paint = """        virtual void paint(juce::Graphics& g) override
        {
            g.setColour(juce::Colours::black);
            g.drawText(getName(), getLocalBounds().withHeight(getHeight()/2), juce::Justification::centredTop);
        }"""
    src = src.replace(old_menu_paint, NEW_UI_MENU_PAINT)

    # 8. Patch uiRadioButton::paint
    old_radio_paint = """        virtual void paint(juce::Graphics& g) override
        {
            g.setColour(juce::Colours::black);
            g.drawText(getName(), getLocalBounds().withHeight(kNameHeight), juce::Justification::centredTop);
        }"""
    src = src.replace(old_radio_paint, NEW_UI_RADIO_PAINT)

    # 9. Patch uiVUMeter::drawVBargraph
    old_vumeter_draw_pattern = r'void drawVBargraph\(juce::Graphics& g, int width, int height\)\s*\{.*?fDB \? drawVBargraphDB \(g, x, width\) : drawVBargraphLin\(g, x, width\);\s*\}'
    if re.search(old_vumeter_draw_pattern, src, re.DOTALL):
        src = re.sub(old_vumeter_draw_pattern, NEW_UI_VUMETER_DRAW, src, flags=re.DOTALL)

    # 9b. Patch uiVUMeter::drawVBargraphDB with downward suppression / notch cut visualization
    old_vumeter_db_pattern = r'void drawVBargraphDB\(juce::Graphics& g, int x, int width\)\s*\{.*?dblevel > dB2Scale\(0\)\)\s*\{.*?\}\s*\}'
    if re.search(old_vumeter_db_pattern, src, re.DOTALL):
        src = re.sub(old_vumeter_db_pattern, NEW_UI_VUMETER_DRAW_DB, src, flags=re.DOTALL)

    # 10. Patch uiVUMeter::drawHBargraph
    old_hbargraph_draw_pattern = r'void drawHBargraph\(juce::Graphics& g, int width, int height\)\s*\{.*?fDB \? drawHBargraphDB \(g, y, height\) : drawHBargraphLin\(g, x, y, width, height\);\s*\}'
    if re.search(old_hbargraph_draw_pattern, src, re.DOTALL):
        src = re.sub(old_hbargraph_draw_pattern, NEW_UI_HBARGRAPH_DRAW, src, flags=re.DOTALL)

    # 11. Patch uiVUMeter::drawNumDisplay
    old_numdisplay_draw_pattern = r'void drawNumDisplay\(juce::Graphics& g, int width, int height\)\s*\{.*?// Text is handled by the setLabelPos\(\) function\s*\}'
    if re.search(old_numdisplay_draw_pattern, src, re.DOTALL):
        src = re.sub(old_numdisplay_draw_pattern, NEW_UI_NUMDISPLAY_DRAW, src, flags=re.DOTALL)

    # 12. Patch uiVUMeter::setupLabel and setLabelPos
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

    # 13. Meter scale text color and size in drawVBargraphDB and drawHBargraphDB
    src = src.replace(
        "g.setFont(9.0f);\n            g.setColour(juce::Colours::white);",
        "g.setFont(juce::Font(juce::FontOptions(8.0f)));\n            g.setColour(juce::Colour(0xff8a8e99));"
    )

    # 14. Editor window background: dark background instead of white
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
