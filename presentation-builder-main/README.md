# Presentation Builder

An AI-powered presentation creation system that transforms scripts into beautiful, Apple-inspired HTML presentations using Claude Code.

## 🎯 Overview

This system allows you to create stunning, professional presentations by simply providing a script and choosing a style reference. Claude will automatically generate a complete HTML presentation with animations, responsive design, and beautiful typography.

## 📁 Project Structure

```
Presentation Builder/
├── scripts/                    # Your presentation scripts go here
├── style-references/           # Reference presentations for styling
├── Finished Presentations/     # Completed presentations are saved here
├── assets/                     # Images and media files
├── CLAUDE.md                   # Claude's design instructions
└── README.md                   # This file
```

## 🚀 Getting Started

### Step 1: Prepare Your Script
1. Write your presentation script in a text file
2. Save it in the `scripts/` folder with a descriptive name (e.g., `software-tailor-script.txt`)

### Step 2: Choose a Style Reference
1. Browse the `style-references/` folder to find a presentation style you like
2. Note the filename of your preferred style

### Step 3: Generate Your Presentation
1. Open Claude Code in this directory
2. Use this command format:
   ```
   Create a new presentation using @scripts/your-script.txt in the style of @style-references/your-chosen-style.html
   ```
3. Claude will automatically generate a beautiful presentation in the `Finished Presentations/` folder

## 🎨 Using Images and Assets

To include images in your presentations:
1. Add image files to the `assets/` folder
2. Tell Claude to use the image: "Use the image @assets/your-image.png for this slide"
3. Claude will incorporate it into the presentation

## ⚙️ Customization

### Refining Claude's Design Approach

The `CLAUDE.md` file contains all design instructions and preferences. To customize:

1. **Color Psychology**: Adjust the color meanings (red for problems, green for solutions, etc.)
2. **Typography**: Modify font sizes, weights, and hierarchy
3. **Animation**: Change animation speeds, delays, and effects
4. **Layout**: Adjust spacing, padding, and grid configurations
5. **Tone**: Fine-tune the presentation style (professional, casual, urgent, etc.)

Simply edit `CLAUDE.md` to bring Claude closer to your preferred design style.

## 📚 Style References

The `style-references/` folder contains example presentations. Each serves as a template for:
- Visual design and color schemes
- Animation patterns
- Layout structures
- Typography choices

## 🎯 Best Practices

1. **Script Writing**:
   - Keep paragraphs focused on single ideas
   - Use clear transitions ("But...", "Therefore...", "Here's the thing...")
   - Include specific data points and examples
   - End with a strong call-to-action

2. **Style Selection**:
   - Match style to content mood (urgent, educational, opportunity-focused)
   - Consider your audience (technical vs non-technical)
   - Review multiple references before choosing

3. **Iteration**:
   - Review generated presentations
   - Update `CLAUDE.md` with refinements
   - Build a library of style references over time

## 📋 Presentation Features

Each generated presentation includes:
- **Responsive Design**: Works on all devices
- **Keyboard Navigation**: Arrow keys and spacebar controls
- **Sequential Animations**: Content reveals step-by-step
- **Professional Typography**: Apple-inspired, clean hierarchy
- **Color Psychology**: Strategic use of colors for impact
- **Lead Magnets**: Conversion-optimized CTAs

## 🔧 Technical Details

Presentations are built with:
- Pure HTML/CSS/JavaScript (no dependencies)
- CSS animations and transitions
- Responsive flexbox and grid layouts
- Custom animation sequencing system
- Mobile-first responsive design

## 💡 Tips

1. **For Complex Topics**: Break into multiple presentations (15-20 slides optimal)
2. **For Data-Heavy Content**: Use the "dense" slide layouts
3. **For Comparisons**: Leverage the side-by-side card system
4. **For Storytelling**: Use progressive reveals and animations

## 🤝 Contributing

To improve the system:
1. Add new style references to expand options
2. Update `CLAUDE.md` with new patterns and best practices
3. Create script templates for common presentation types

## 📝 License

This project is for personal and commercial use. Feel free to customize and extend as needed.

---

**Created by Zane Schulberg** | Powered by Claude Code