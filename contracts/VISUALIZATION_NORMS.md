# ATLAS Visualization Norms

*Canonical reference for all figures, charts, diagrams, and tables produced by ATLAS.*
*Last updated: 2026-03-02*

**Audience calibration**: Smart 3rd-year undergraduate who has taken intro stats and one lab methods course. They can read a scatter plot but shouldn't need to decode a figure. Every figure should be interpretable in under 10 seconds of scanning.

---

## 1. Core Principles

### 1.1 Tufte's Data-Ink Ratio

Every drop of ink on a figure should represent data or essential structure. Eliminate:
- 3D effects (always)
- Gradient fills (always)
- Decorative gridlines (use sparse, light gridlines only if they aid reading exact values)
- Chart borders and boxes (open axes preferred)
- Moiré patterns, hatching, or textured fills
- Drop shadows, bevels, embossing

The test: cover any element with your thumb. If the figure loses information, keep it. If nothing is lost, remove it.

### 1.2 Cleveland & McGill's Perceptual Hierarchy

Encode the most important variable using the most accurately perceived visual channel:

1. **Position on a common scale** (most accurate — use for primary comparisons)
2. **Position on non-aligned scales** (use for small multiples)
3. **Length** (bar charts — good for magnitude comparison)
4. **Angle / slope** (line charts — good for trends)
5. **Area** (bubble charts — use sparingly, humans underestimate area)
6. **Color saturation / luminance** (heat maps — supplement with numbers)
7. **Color hue** (categorical only — never for quantitative data)

Practical implication: if you're deciding between a pie chart and a bar chart, always choose the bar chart. If you're deciding between a stacked area chart and small multiples, choose small multiples.

### 1.3 Gestalt Grouping

Use the viewer's perceptual system to organize information:
- **Proximity**: Related items close together, unrelated items separated
- **Similarity**: Same category = same color/shape; different category = different
- **Continuity**: Guide the eye along smooth lines, not jagged jumps
- **Enclosure**: Use subtle background shading (not boxes) to group related elements
- **Connection**: Lines connecting related elements are perceived as grouped before proximity

### 1.4 The 10-Second Rule

A reader should be able to extract the main message of any figure within 10 seconds of looking at it. This means:
- The title/caption tells them what to look for
- The most important pattern is visually salient (largest, highest contrast, most central)
- Labels are direct (on the data) rather than indirect (in a legend requiring eye movement)
- No decoding is needed — the figure is self-explanatory

---

## 2. Color

### 2.1 Palette

Use this ATLAS standard palette (colorblind-safe, tested for deuteranopia and protanopia):

```
Primary:    #2171B5 (blue)       — default for single-series data
Secondary:  #CB4335 (brick red)  — contrast/comparison
Tertiary:   #27AE60 (green)      — third category
Quaternary: #F39C12 (amber)      — fourth category
Accent:     #8E44AD (purple)     — highlights, annotations
Neutral:    #7F8C8D (gray)       — baselines, reference lines
Background: #FFFFFF (white)      — always white, never gray
```

For sequential data (heat maps, gradients): use `viridis` or `cividis` (both colorblind-safe).

For diverging data (positive/negative): use blue (#2171B5) → white → red (#CB4335).

### 2.2 Rules

- Never encode information in red-green contrast alone
- Always have a non-color redundant encoding (shape, pattern, label)
- Use luminance variation, not just hue variation, so figures work in grayscale
- Maximum 6 colors in any single figure; prefer 3-4
- WCAG 2.1 AA contrast: all text/data must have ≥4.5:1 contrast against background

### 2.3 Accessibility Test

Before finalizing, view through a deuteranopia simulator (e.g., Coblis). If any two categories become indistinguishable, add redundant encoding.

---

## 3. Typography

### 3.1 Fonts

- **Axis labels and annotations**: Sans-serif (Helvetica, Arial, DejaVu Sans). Size ≥ 9pt at final print size.
- **Mathematical notation**: Proper italic for variables (use matplotlib's mathtext or LaTeX): *P(x)*, *C**, *σ*
- **Titles**: Bold sans-serif, 11-12pt
- **Captions**: Serif (Times, Cambria) matching body text, 10pt

### 3.2 Label Placement

- **Direct labeling** preferred over legends. Place the label next to the data it describes.
- If a legend is necessary (>4 series), place it inside the plot area in a low-data region, not outside.
- Never make the reader match colors between a legend and data by memory — minimize eye travel.
- Axis labels: always include units. "Temperature (°C)" not "Temperature". "Fractal dimension *D*" not just "*D*".

---

## 4. Figure Types and When to Use Them

### 4.1 XY Scatter / Line Plot
**Use when**: Showing relationship between two continuous variables
**Rules**: Points for discrete data; lines for continuous/modeled data; both for data + fit. Always show confidence bands for fitted curves.

### 4.2 Bar Chart
**Use when**: Comparing discrete categories on a single quantity
**Rules**: Horizontal bars for >5 categories (easier to read labels). Always start y-axis at zero. Order bars by value (not alphabetically) unless there's a natural ordering.

### 4.3 Small Multiples
**Use when**: Comparing the same pattern across subgroups
**Rules**: Same axis scales across all panels. Shared axis labels. Panels arranged in reading order (left-to-right, top-to-bottom). 2×3 or 3×3 grids preferred.

### 4.4 Heat Map / Matrix
**Use when**: Showing patterns in 2D categorical data (e.g., modality × evidence type)
**Rules**: Use sequential colormap for single-valence data, diverging for positive/negative. Always annotate cells with values. Sort rows and columns by a meaningful variable (not alphabetically).

### 4.5 Box-and-Arrow Diagrams (Boxology)
**Use when**: Showing system architecture, information flow, or theoretical relationships
**Rules**:
- Boxes: rounded rectangles, minimal text (2-4 words per box), consistent size
- Arrows: directional, labeled if the relationship type matters
- Layers: use vertical separation for levels of description (functional → neural → theoretical)
- Color: use color to group by category, not for decoration
- Flow direction: top-to-bottom or left-to-right (never mixed)
- Maximum boxes per figure: 12 (beyond this, split into sub-figures)

### 4.6 Venn / Euler Diagrams
**Use when**: Showing set relationships (overlap, intersection, complement)
**Rules**: Maximum 4 sets (beyond this, use a matrix instead). Label intersection regions. Use area approximately proportional to set size when possible.

### 4.7 Infographic Bars
**Use when**: Showing ranges, targets, or zones along a scale
**Rules**: Horizontal orientation. Mark the "target zone" with a distinct fill. Annotate specific values. Include reference points the reader can relate to.

### 4.8 Tables
**Use when**: Exact values matter more than visual patterns
**Rules**: Right-align numbers. Use consistent decimal places. Bold key values. Horizontal rules only (top, header-separator, bottom — no vertical rules, no full grid). Sort rows meaningfully.

---

## 5. Captions — The Scientific American Standard

Every figure caption must be self-contained. A reader should be able to understand the paper's argument by reading only the captions and studying the figures. This is the Scientific American standard.

### 5.1 Structure (3-6 sentences)

1. **Sentence 1**: What the figure shows (the "what"). Start with the figure's subject, not "This figure shows..."
   - Good: "The inverted-U function appears across all five sensory modalities."
   - Bad: "This figure shows the inverted-U function."

2. **Sentence 2-3**: What the key finding or pattern is (the "so what"). What should the reader notice?
   - "Visual complexity peaks at fractal dimension D ≈ 1.3, matching the statistics of natural scenes."

3. **Sentence 4-5**: Why it matters or what it implies (the "now what"). Connect to the paper's argument.
   - "This convergence supports the efficient coding hypothesis and provides a concrete design target for architects."

4. **Sentence 6** (optional): Caveats or scope conditions.
   - "Cross-cultural data remain sparse; the shaded zones reflect primarily Western samples."

### 5.2 Rules

- Never say "This figure shows..." — start with the content itself
- Include enough information that the caption + figure is self-explanatory
- Reference specific values, ranges, or patterns visible in the figure
- Include the source of data if not original ("data from Taylor et al., 1999")
- Include units for all quantitative claims
- Bold key terms on first use in the caption

---

## 6. Common Mistakes to Avoid

1. **Dual y-axes**: Almost always misleading. Use small multiples instead.
2. **Truncated y-axes on bar charts**: Always start at zero for bar charts (not for line charts).
3. **Rainbow colormaps**: Never use jet/rainbow — they create false boundaries and are colorblind-hostile.
4. **Pie charts**: Almost never appropriate. Use bar charts.
5. **3D anything**: Never use 3D unless the data is genuinely three-dimensional (e.g., a surface plot of f(x,y)).
6. **Overplotting**: If points overlap, use transparency (alpha), jitter, or density contours.
7. **Missing units**: Every axis must have units. No exceptions.
8. **Legends far from data**: If the legend requires eye movement across the figure, redesign.
9. **Too many categories**: If a figure has >7 categories, the reader cannot track them. Simplify.
10. **Inconsistent scales across panels**: Small multiples MUST share axis scales.

---

## 7. Production Specifications

### 7.1 File Format
- **Working format**: SVG (scalable, editable)
- **Submission format**: PDF or EPS (vector) at 300 DPI for raster elements
- **Web/Streamlit**: PNG at 2× resolution (retina)

### 7.2 Dimensions
- **Single column**: 3.3 inches (84 mm) wide
- **Double column**: 6.9 inches (175 mm) wide
- **Maximum height**: 9.0 inches (230 mm)

### 7.3 Resolution
- **Line art**: Vector (infinite resolution)
- **Photographic elements**: 300 DPI minimum
- **Screen display**: 150 DPI minimum

---

## 8. Implementation

When generating figures programmatically, use this matplotlib configuration:

```python
import matplotlib.pyplot as plt
import matplotlib as mpl

# ATLAS figure style
ATLAS_STYLE = {
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'axes.edgecolor': '#333333',
    'axes.linewidth': 0.8,
    'axes.grid': False,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'font.family': 'sans-serif',
    'font.sans-serif': ['Helvetica', 'Arial', 'DejaVu Sans'],
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'lines.linewidth': 1.5,
    'lines.markersize': 5,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.1,
}

ATLAS_COLORS = {
    'primary': '#2171B5',
    'secondary': '#CB4335',
    'tertiary': '#27AE60',
    'quaternary': '#F39C12',
    'accent': '#8E44AD',
    'neutral': '#7F8C8D',
}

def apply_atlas_style():
    mpl.rcParams.update(ATLAS_STYLE)
```

---

## 9. Review Checklist

Before finalizing any figure, verify:

- [ ] Can you state the figure's message in one sentence?
- [ ] Does the caption pass the self-contained test (interpretable without body text)?
- [ ] Is the most important pattern the most visually salient element?
- [ ] Are all axes labeled with units?
- [ ] Is the color palette colorblind-safe?
- [ ] Does the figure work in grayscale (for print)?
- [ ] Are labels direct (on data) rather than requiring legend lookup?
- [ ] Is the data-ink ratio high (>70% of ink is data)?
- [ ] Are all text elements readable at final print size?
- [ ] Does the figure respect WCAG 2.1 AA contrast ratios?
