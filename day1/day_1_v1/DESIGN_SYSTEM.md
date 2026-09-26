# ALCOA+ Design System Documentation

## Overview

The ALCOA+ Data Integrity Framework uses a modern, professional design system tailored for pharmaceutical operations compliance and educational purposes.

## Design Philosophy

- **User-Centered**: Easy to understand and navigate
- **Professional**: Pharmaceutical-grade aesthetic
- **Accessible**: WCAG compliance standards
- **Responsive**: Works seamlessly on all devices
- **Performance-Focused**: No external dependencies

## Color System

### Primary Colors
| Color | Hex | Usage | WCAG AA | WCAG AAA |
|-------|-----|-------|---------|----------|
| Primary Purple | #667eea | Primary actions, highlights | ✅ | ✅ |
| Secondary Purple | #764ba2 | Secondary elements | ✅ | ✅ |
| Success Green | #28a745 | Pass status, positive states | ✅ | ✅ |
| Warning Yellow | #ffc107 | In-progress status, warnings | ⚠️ | ⚠️ |
| Danger Red | #dc3545 | Fail status, critical items | ✅ | ✅ |

### Principle Colors
Each of the 9 ALCOA+ principles has a unique color for visual distinction:

| Principle | Color | Hex |
|-----------|-------|-----|
| Attributable | Purple | #667eea |
| Legible | Darker Purple | #764ba2 |
| Contemporaneous | Red | #e74c3c |
| Original | Blue | #3498db |
| Accurate | Teal | #16a085 |
| Complete | Orange | #d35400 |
| Consistent | Violet | #8e44ad |
| Enduring | Dark Red | #c0392b |
| Available | Navy | #2980b9 |

### Neutral Colors
| Color | Hex | Usage |
|-------|-----|-------|
| White | #ffffff | Backgrounds, text on dark |
| Light Gray | #f5f7fa | Secondary backgrounds |
| Medium Gray | #e8ecf1 | Borders, subtle dividers |
| Dark Gray | #2c3e50 | Primary text |
| Black | #000000 | Text, strong emphasis |

### Gradient System

#### Primary Gradient
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```
Used for: Headers, primary buttons, active states

#### Success Gradient
```css
background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
```
Used for: Pass badges, positive indicators

#### Warning Gradient
```css
background: linear-gradient(135deg, #ffc107 0%, #ff9800 100%);
```
Used for: In-progress status, warnings

#### Danger Gradient
```css
background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
```
Used for: Fail badges, critical items

## Typography System

### Font Stack
```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
```

### Font Sizes
| Size | Value | Usage |
|------|-------|-------|
| H1 | 2.8rem (44.8px) | Page title |
| H2 | 2.2rem (35.2px) | Section heading |
| H3 | 1.8rem (28.8px) | Subsection heading |
| H4 | 1.4rem (22.4px) | Card title |
| Body | 1rem (16px) | Regular text |
| Small | 0.875rem (14px) | Secondary text |
| Tiny | 0.75rem (12px) | Labels, metadata |

### Font Weights
| Weight | Value | Usage |
|--------|-------|-------|
| Light | 300 | Subtle, decorative |
| Regular | 400 | Body text |
| Medium | 500 | Emphasis, labels |
| Semibold | 600 | Subheadings |
| Bold | 700 | Strong emphasis |

### Letter Spacing
| Level | Value | Usage |
|-------|-------|-------|
| Tight | -0.5px | Headings |
| Normal | 0px | Body text |
| Relaxed | 0.5px | Labels, UI text |
| Wide | 1px | Special emphasis |

### Line Height
| Level | Value | Usage |
|-------|-------|-------|
| Tight | 1.2 | Headings |
| Normal | 1.5 | Body text |
| Relaxed | 1.8 | Long-form content |

## Spacing System

### Base Unit: 30px

| Multiple | Value | Usage |
|----------|-------|-------|
| 0.5x | 15px | Small gaps |
| 1x | 30px | Standard padding |
| 1.5x | 45px | Large sections |
| 2x | 60px | Section separation |
| 3x | 90px | Major breaks |

### Common Spacing Values
- **Micro**: 8px (very small gaps)
- **Small**: 15px (small padding)
- **Medium**: 30px (standard)
- **Large**: 45px (generous spacing)
- **XL**: 60px (section breaks)

## Border System

### Border Radius
| Size | Value | Usage |
|------|-------|-------|
| Small | 8px | Subtle curves |
| Medium | 12px | Default (most elements) |
| Large | 16px | Cards, containers |
| XL | 20px | Large components |
| Full | 50% | Badges, circles |

### Border Styles
| Style | Value | Usage |
|-------|-------|-------|
| Subtle | 1px solid #e8ecf1 | Light separators |
| Medium | 2px solid #667eea | Accent borders |
| Heavy | 3px solid #764ba2 | Strong emphasis |

### Principle Card Border
```css
border-left: 4px solid [principle-color];
border-radius: 12px;
```

## Shadow System

### Shadow Depth Levels

#### Subtle (Level 1)
```css
box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
```
Used for: Hover states, subtle elevation

#### Medium (Level 2)
```css
box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
```
Used for: Default card shadow, moderate elevation

#### Elevated (Level 3)
```css
box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
```
Used for: Modal shadows, strong elevation

#### Deep (Level 4)
```css
box-shadow: 0 12px 24px rgba(0, 0, 0, 0.25);
```
Used for: Maximum elevation, deep emphasis

## Component Styles

### Buttons

#### Primary Button
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
color: white;
padding: 12px 24px;
border-radius: 8px;
border: none;
cursor: pointer;
transition: all 0.3s ease;
```

Hover State:
```css
transform: translateY(-2px);
box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
```

#### Secondary Button
```css
background: #f5f7fa;
color: #2c3e50;
padding: 12px 24px;
border-radius: 8px;
border: 1px solid #e8ecf1;
cursor: pointer;
```

### Cards

#### Standard Card
```css
background: white;
border-radius: 12px;
padding: 30px;
box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
border: 1px solid #e8ecf1;
```

Hover State:
```css
transform: translateY(-4px);
box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
```

### Badges

#### Success Badge
```css
background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
color: white;
padding: 8px 12px;
border-radius: 20px;
font-size: 0.85rem;
font-weight: 600;
```

#### Warning Badge
```css
background: linear-gradient(135deg, #ffc107 0%, #ff9800 100%);
color: white;
padding: 8px 12px;
border-radius: 20px;
font-size: 0.85rem;
font-weight: 600;
```

#### Danger Badge
```css
background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
color: white;
padding: 8px 12px;
border-radius: 20px;
font-size: 0.85rem;
font-weight: 600;
```

### KPI Cards

#### Structure
```css
{
  background: white;
  border-left: 4px solid [color];
  border-radius: 12px;
  padding: 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
```

#### Label
```css
{
  font-size: 0.95rem;
  color: #7f8c8d;
  font-weight: 500;
  letter-spacing: 0.5px;
}
```

#### Value
```css
{
  font-size: 2.8em;
  font-weight: 700;
  color: #2c3e50;
  line-height: 1.2;
}
```

### Tables

#### Header Style
```css
{
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 18px;
  font-weight: 600;
  text-align: left;
  text-transform: uppercase;
  font-size: 0.85rem;
  letter-spacing: 1px;
}
```

#### Row Style
```css
{
  padding: 18px;
  border-bottom: 1px solid #e8ecf1;
}
```

Row Hover:
```css
{
  background-color: #f9f9f9;
  transition: background-color 0.2s ease;
}
```

### Dropdowns

#### Container
```css
{
  position: relative;
  display: block;
  margin-top: 10px;
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.3s ease, opacity 0.3s ease;
  opacity: 0;
}
```

Active State:
```css
{
  max-height: 500px;
  opacity: 1;
}
```

#### Content
```css
{
  background: #f5f7fa;
  border-left: 4px solid [principle-color];
  padding: 20px;
  border-radius: 8px;
  margin-top: 10px;
}
```

## Responsive Design

### Breakpoints
| Device | Breakpoint | Usage |
|--------|-----------|-------|
| Desktop | 1024px+ | Default layout |
| Tablet | 768px - 1023px | Medium adjustments |
| Mobile | Below 768px | Mobile layout |

### Tablet Adjustments (@media max-width: 768px)
```css
/* Reduced padding */
padding: 20px;

/* Adjusted font sizes */
h1 { font-size: 2rem; }
h2 { font-size: 1.6rem; }

/* Stack layout */
display: flex;
flex-direction: column;

/* Better spacing */
gap: 20px;
```

### Mobile Adjustments (@media max-width: 480px)
```css
/* Minimal padding */
padding: 15px;

/* Reduced font sizes */
h1 { font-size: 1.8rem; }
body { font-size: 14px; }

/* Full-width elements */
width: 100%;

/* Larger touch targets */
min-height: 44px;
```

## Animations & Transitions

### Standard Transition
```css
transition: all 0.3s ease;
```

### Hover Effects
```css
/* Translation on hover */
transform: translateY(-2px);

/* Shadow enhancement */
box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);

/* Scale effect */
transform: scale(1.05);
```

### Dropdown Animation
```css
/* Slide in */
transition: max-height 0.3s ease, opacity 0.3s ease;
```

## Accessibility

### Color Contrast Ratios
- **AA Standard**: 4.5:1 for normal text, 3:1 for large text
- **AAA Standard**: 7:1 for normal text, 4.5:1 for large text

### Touch Targets
- **Minimum Size**: 44px x 44px (mobile)
- **Desktop**: 40px x 40px

### Keyboard Navigation
- Tab order follows visual hierarchy
- All interactive elements focusable
- Visible focus indicators

### Screen Reader Support
- Semantic HTML structure
- ARIA labels on custom components
- Descriptive link text

## Usage Guidelines

### When to Use Principle Colors
- Primary card border for principle identification
- Status indicators for principle compliance
- Visual hierarchy in dashboards
- Group-related content

### When to Use Gradients
- Primary actions
- Section headers
- Status badges
- Emphasis elements

### When to Use Shadows
- Card elevation
- Hover states for depth
- Modal overlays
- Interactive feedback

### Spacing Best Practices
- Use consistent multiples of base unit (30px)
- Maintain breathing room around text
- Group related content with smaller gaps
- Separate sections with larger gaps

### Typography Hierarchy
- H1: Page title (one per page)
- H2: Main sections
- H3: Subsections
- H4: Card/component titles
- Body: Regular content

## Customization

### Brand Customization
To adapt the design system for a different brand:

1. **Update color variables** in CSS
2. **Modify gradient definitions**
3. **Adjust font family** if needed
4. **Update logo/branding** in header
5. **Modify principle colors** for your framework

### Example: New Primary Color
```css
/* Old */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* New */
background: linear-gradient(135deg, #your-color-1 0%, #your-color-2 100%);
```

## Maintenance

### Regular Updates
- Review color contrast ratios annually
- Update accessibility standards as needed
- Refresh animations based on browser capabilities
- Monitor responsive breakpoints

### Browser Support
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- IE 11 (limited support)

---

*Design System Version: 1.0*
*Last Updated: 2026-08-29*
*Compliance: WCAG 2.1 Level AA*
