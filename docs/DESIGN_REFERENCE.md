# 🌙 Design Reference — "Astro Essence"

> A calm, celestial, and elegant design system for a mature astrology application

## Vision

Create a design that is:

- 🌌 **Calm & Celestial** — Soft gradients, lunar palette, ethereal atmosphere
- ✨ **Elegant** — Classic typography, thin lines, generous spacing
- 👤 **Mature** — Targeting 30–45 demographic with sophistication
- 🏆 **Trustable & Premium** — Clean layouts, subtle animations, focus on readability
- 🎨 **Figma-Friendly** — All design tokens are easily importable to Figma

---

## 🎨 1. Visual Identity

### Color Palette — Premium Celestial

A sophisticated palette that avoids pink while maintaining feminine elegance:

| Purpose | Color | Hex | Usage |
|---------|-------|-----|-------|
| **Primary** | Indigo Blue | `#4A5FC1` | CTAs, links, primary actions, planet highlights |
| **Secondary** | Muted Lavender | `#C8A2C8` | Secondary buttons, accents, gentle highlights |
| **Accent** | Soft Ivory | `#F4EDE2` | Cards backgrounds, gentle contrast areas |
| **Background Light** | Pure White Tint | `#FAFAFF` | Main background |
| **Background Gradient** | Celestial Fade | `linear-gradient(180deg, #FDFBFF 0%, #F3F6FF 100%)` | Page backgrounds, hero sections |
| **Text Dark** | Deep Charcoal | `#2B2B38` | Primary text, headings |
| **Text Muted** | Soft Gray | `#6B7280` | Secondary text, descriptions |
| **Line/Border** | Subtle Gray | `#D8DAE5` | Dividers, borders, subtle separators |

### Extended Palette

**Planet Colors** (for chart visualization):
- Sun: `#F59E0B` (Amber)
- Moon: `#93C5FD` (Sky Blue)
- Mercury: `#A78BFA` (Purple)
- Venus: `#F9A8D4` (Pink)
- Mars: `#EF4444` (Red)
- Jupiter: `#3B82F6` (Blue)
- Saturn: `#64748B` (Slate)
- Uranus: `#06B6D4` (Cyan)
- Neptune: `#8B5CF6` (Violet)
- Pluto: `#7C3AED` (Purple)

**Semantic Colors**:
- Success: `#10B981` (Green)
- Warning: `#F59E0B` (Amber)
- Error: `#EF4444` (Red)
- Info: `#3B82F6` (Blue)

---

## ✨ 2. Typography

### Font Families

A combination that feels both astrological and elegant:

**Headings**: [Playfair Display](https://fonts.google.com/specimen/Playfair+Display)
- Serif, refined, evokes classical astrology texts
- Weights: Regular (400), Semibold (600), Bold (700)

**Body Text**: [Inter](https://fonts.google.com/specimen/Inter)
- Clean, highly readable, modern
- Weights: Regular (400), Medium (500), Semibold (600)

**Alternative Body**: [Lato](https://fonts.google.com/specimen/Lato)
- Warm, friendly, professional
- Use if Inter feels too geometric

**Numbers & Data**: [Inter Tight](https://fonts.google.com/specimen/Inter+Tight)
- For planetary positions, degrees, coordinates
- More compact for tabular data

### Type Scale

| Element | Font | Size | Weight | Line Height | Letter Spacing |
|---------|------|------|--------|-------------|----------------|
| **H1 — Page Title** | Playfair Display | 38px | Semibold (600) | 1.2 | -0.02em |
| **H2 — Section Title** | Playfair Display | 28px | Semibold (600) | 1.3 | -0.01em |
| **H3 — Subsection** | Playfair Display | 22px | Semibold (600) | 1.4 | 0 |
| **H4 — Card Title** | Inter | 18px | Semibold (600) | 1.4 | -0.01em |
| **Body Large** | Inter | 16px | Regular (400) | 1.6 | 0 |
| **Body** | Inter | 15px | Regular (400) | 1.6 | 0 |
| **Body Small** | Inter | 14px | Regular (400) | 1.5 | 0 |
| **Caption** | Inter | 13px | Medium (500) | 1.4 | 0.01em |
| **Label** | Inter | 12px | Medium (500) | 1.3 | 0.04em (uppercase) |
| **Data/Numbers** | Inter Tight | 15px | Medium (500) | 1.4 | 0 |

### Typographic Principles

- **Generous spacing**: Minimum 1.5 line height for body text
- **Hierarchy through weight**: Use font weight before size changes
- **Limited font sizes**: Stick to the scale above, max 6–7 sizes per page
- **Serif for emotion**: Use Playfair Display to add warmth and personality
- **Sans-serif for clarity**: Use Inter for data, forms, and UI elements

---

## 🌌 3. Spacing & Layout

### Spacing Scale (8px base)

| Token | Value | Usage |
|-------|-------|-------|
| `xs` | 4px | Tight spacing, icon gaps |
| `sm` | 8px | Small gaps, inline elements |
| `md` | 16px | Default spacing between elements |
| `lg` | 24px | Section spacing, card padding |
| `xl` | 32px | Large section gaps |
| `2xl` | 48px | Major section separation |
| `3xl` | 64px | Page-level spacing |
| `4xl` | 96px | Hero sections |

### Grid System

- **Desktop**: 12-column grid, 1440px max-width
- **Tablet**: 8-column grid, 1024px max-width
- **Mobile**: 4-column grid, 375px min-width
- **Gutter**: 24px (desktop), 16px (mobile)
- **Margin**: 80px (desktop), 24px (mobile)

### Container Widths

- **Full Width**: 1440px
- **Content Width**: 1200px
- **Reading Width**: 720px (for long-form text)
- **Form Width**: 480px (for forms and modals)

---

## 🎭 4. UI Components

### Buttons

**Primary Button**:
```css
background: #4A5FC1
color: white
padding: 12px 24px
border-radius: 12px
font: Inter Medium 15px
box-shadow: 0 4px 12px rgba(74, 95, 193, 0.2)
transition: all 0.2s ease

hover:
  transform: translateY(-2px)
  box-shadow: 0 8px 24px rgba(74, 95, 193, 0.3)
```

**Secondary Button**:
```css
background: transparent
color: #4A5FC1
border: 1.5px solid #4A5FC1
padding: 12px 24px
border-radius: 12px
font: Inter Medium 15px

hover:
  background: #F3F6FF
  border-color: #3A4FB1
```

**Subtle Button**:
```css
background: #F7F7FC
color: #2B2B38
padding: 10px 20px
border-radius: 10px
font: Inter Medium 14px

hover:
  background: #EDEDF5
```

### Cards

**Standard Card**:
```css
background: white
padding: 24px
border-radius: 20px
border: 1px solid #D8DAE5
box-shadow: 0 2px 8px rgba(43, 43, 56, 0.04)
transition: all 0.3s ease

hover:
  transform: translateY(-4px)
  box-shadow: 0 8px 24px rgba(43, 43, 56, 0.12)
  border-color: #C8A2C8
```

**Premium Card** (for important content):
```css
background: linear-gradient(135deg, #FDFBFF 0%, #F9F6FF 100%)
padding: 32px
border-radius: 24px
border: 2px solid #C8A2C8
box-shadow: 0 4px 16px rgba(200, 162, 200, 0.15)
```

### Form Inputs

**Text Input**:
```css
background: #F7F7FC
border: 1.5px solid #D8DAE5
border-radius: 12px
padding: 14px 16px
font: Inter Regular 15px
color: #2B2B38

focus:
  background: white
  border-color: #4A5FC1
  box-shadow: 0 0 0 4px rgba(74, 95, 193, 0.1)
```

**Label**:
```css
font: Inter Medium 13px
color: #2B2B38
text-transform: uppercase
letter-spacing: 0.04em
margin-bottom: 8px
```

### Modals

```css
background: white
padding: 40px
border-radius: 24px
max-width: 600px
box-shadow: 0 24px 64px rgba(43, 43, 56, 0.2)

backdrop:
  background: rgba(43, 43, 56, 0.5)
  backdrop-filter: blur(8px)
```

---

## 🔮 5. Screen-by-Screen Design Guide

### 🌟 Login Page

**Current Issues**:
- Looks generic and impersonal
- No brand identity or personality
- Lacks premium feel

**Redesign Vision**:

**Layout**: Split screen (60/40)

**Left Side** (60%):
```
Background: linear-gradient(135deg, #4A5FC1 0%, #C8A2C8 100%)
Overlay: Subtle constellation pattern (opacity 10%)
Content:
  - Logo (white, 48px height)
  - Tagline: "Autoconhecimento com precisão astrológica"
  - Decorative element: Minimal star map illustration
```

**Right Side** (40%):
```
Background: White
Card:
  - Padding: 48px
  - Border radius: 24px
  - Shadow: 0 16px 48px rgba(43, 43, 56, 0.12)

Content:
  - H1: "Bem-vindo de volta" (Playfair Display 38px)
  - Subtitle: "Entre para acessar seus mapas natais"
  - Form fields with soft backgrounds (#F7F7FC)
  - OAuth buttons with icons + subtle borders
  - Footer link: "Não tem conta? Criar conta"
```

**Enhancements**:
- Add subtle fade-in animation (0.4s ease)
- Input focus states with soft glow
- Smooth transitions on hover states

---

### 📝 New Map Form

**Current Issues**:
- Too "system form", bureaucratic feeling
- Lacks flow and visual hierarchy
- No guidance or microcopy
- Overwhelming single-page form

**Redesign Vision**:

**Multi-Step Form** (4 steps):

**Step 1 — Dados Pessoais**:
```
Fields:
  - Nome completo
  - Gênero (optional)
  - Tipo de mapa (nascimento/sinastria/etc.)

Microcopy: "Quem é a pessoa?"
Icon: 👤 (subtle, left of title)
```

**Step 2 — Nascimento**:
```
Fields:
  - Data de nascimento (date picker com calendar UI)
  - Hora (time picker com relógio visual)
  - Fuso horário (auto-detect + manual)

Microcopy: "Quando você nasceu?"
Helper text: "Quanto mais preciso, melhor o mapa"
Icon: 🌙
```

**Step 3 — Localização**:
```
Fields:
  - Cidade (autocomplete com bandeiras de países)
  - Latitude/Longitude (auto-fill)
  - Sugestões populares (São Paulo, Rio, etc.)

Microcopy: "Onde você nasceu?"
Map preview: Small static map showing location
Icon: 📍
```

**Step 4 — Revisão**:
```
Summary card with:
  - All entered data
  - Preview of Ascendant sign
  - "Calcular Mapa" button (larger, primary)

Microcopy: "Tudo certo?"
```

**Visual Elements**:
- Progress indicator: Dots (4) with fade line between
- Back/Next buttons: Clear hierarchy
- Section cards with subtle shadows
- Inline validation with gentle green checks
- Tooltip icons (ⓘ) with 1.5px stroke

**Spacing**:
- Form fields: 20px gap
- Section padding: 32px
- Step-to-step transition: Fade + slide (0.3s)

---

### 🗂️ My Maps Page (Cards Grid)

**Current Issues**:
- Cards feel plain and utilitarian
- No emotional connection
- Limited visual information
- Generic card design

**Redesign Vision**:

**Grid Layout**:
- Desktop: 3 columns
- Tablet: 2 columns
- Mobile: 1 column
- Gap: 24px

**Card Design**:
```css
Card:
  padding: 28px
  border-radius: 20px
  background: white
  border: 1.5px solid #D8DAE5
  box-shadow: 0 2px 8px rgba(43, 43, 56, 0.06)
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1)

Hover:
  transform: translateY(-6px)
  box-shadow: 0 12px 32px rgba(74, 95, 193, 0.15)
  border-color: #C8A2C8
  background: linear-gradient(135deg, #FFFFFF 0%, #F9F6FF 100%)
```

**Card Content Structure**:
```
┌─────────────────────────────────┐
│ 👤 Nome da Pessoa               │
│ Playfair Display 22px           │
│                                 │
│ ☉ Sol • ☽ Lua • ↑ Ascendente   │
│ [Leão] [Aquário] [Áries]       │
│ Inter 14px, lavender badges     │
│                                 │
│ 📍 São Paulo, Brasil            │
│ Inter 13px, muted               │
│                                 │
│ ────────────────────────────── │
│                                 │
│ Criado em 10/11/2021            │
│ Último acesso há 3 dias         │
│ Inter 12px, subtle gray         │
│                                 │
│ [Ver Detalhes] [•••]           │
└─────────────────────────────────┘
```

**Visual Elements**:
- **Planet Icons**: Use symbols (☉ ☽ ☿) in soft lavender circles
- **Badges**: Sign names in rounded badges with pastel backgrounds
- **Divider**: Thin line (1px, #D8DAE5, opacity 50%)
- **Action Button**: "Ver Detalhes" with arrow icon →
- **More Menu**: Three dots (•••) with dropdown

**Empty State**:
```
Icon: Large constellation illustration (pastel colors)
Heading: "Nenhum mapa criado ainda"
Subtext: "Crie seu primeiro mapa natal e descubra seu céu de nascimento"
CTA: "Criar Primeiro Mapa" (primary button)
```

---

### 🌙 Chart Detail Page

**Current Status**: Good foundation with Big Three cards

**Enhancements**:

**Big Three Cards** (already implemented):
```
Refinements:
  - Add subtle gradient animation on hover
  - Increase symbol size to 36px
  - Add decorative dot separator •
  - Example: "Sol • Identidade"
```

**Chart Wheel**:
```
Enhancements:
  - Add subtle shadow behind wheel
  - Glow effect on planet symbols (on hover)
  - Smooth zoom interaction (optional)
  - Legend card below with color meanings
```

**Tabs**:
```
Visual Update:
  - Larger tab text (16px)
  - Add icons before text (🌟 Visualização, etc.)
  - Active tab: Gradient underline (3px, primary → secondary)
  - Smooth slide transition
```

**Data Tables**:
```
Styling:
  - Alternating row background (#F7F7FC every other row)
  - Hover state: subtle lavender highlight
  - Icons in first column (planet/house symbols)
  - Aligned numbers with monospace font
```

---

## 🎬 6. Animations & Transitions

### Timing Functions

```css
--ease-smooth: cubic-bezier(0.4, 0, 0.2, 1)
--ease-out: cubic-bezier(0, 0, 0.2, 1)
--ease-in: cubic-bezier(0.4, 0, 1, 1)
--ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55)
```

### Standard Transitions

| Element | Property | Duration | Easing |
|---------|----------|----------|--------|
| Buttons | background, transform | 200ms | ease-smooth |
| Cards | transform, shadow | 300ms | ease-smooth |
| Modals | opacity, scale | 250ms | ease-out |
| Page transitions | opacity | 400ms | ease-smooth |
| Tooltips | opacity | 150ms | ease-out |

### Micro-interactions

**Button Hover**:
```css
transform: translateY(-2px)
box-shadow: enhanced
transition: 200ms ease-smooth
```

**Card Hover**:
```css
transform: translateY(-4px) scale(1.01)
box-shadow: elevated
transition: 300ms ease-smooth
```

**Input Focus**:
```css
border-color: primary
box-shadow: 0 0 0 4px rgba(primary, 0.1)
transition: 150ms ease-out
```

**Page Load**:
```css
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
animation: fadeIn 0.4s ease-smooth
```

### Loading States

**Spinner**:
```css
border: 3px solid rgba(74, 95, 193, 0.1)
border-top-color: #4A5FC1
border-radius: 50%
animation: spin 0.8s linear infinite
```

**Skeleton Screens**:
```css
background: linear-gradient(
  90deg,
  #F7F7FC 0%,
  #EDEDF5 50%,
  #F7F7FC 100%
)
animation: shimmer 1.5s infinite
```

---

## 📱 7. Responsive Design

### Breakpoints

```css
/* Mobile */
@media (max-width: 640px) {
  /* Stack layouts, full-width cards */
}

/* Tablet */
@media (min-width: 641px) and (max-width: 1024px) {
  /* 2-column grids */
}

/* Desktop */
@media (min-width: 1025px) {
  /* 3-column grids, larger spacing */
}

/* Large Desktop */
@media (min-width: 1440px) {
  /* Max-width constraints, centered content */
}
```

### Mobile Considerations

- **Touch Targets**: Minimum 44px × 44px
- **Font Sizes**: Minimum 16px to prevent zoom on iOS
- **Spacing**: Reduce by 33% on mobile (24px → 16px)
- **Navigation**: Sticky bottom nav or hamburger menu
- **Forms**: Single column, larger inputs
- **Modals**: Full-screen on mobile (slide up)

---

## 🌟 8. Iconography

### Icon Style

- **Style**: Outline (not filled)
- **Stroke Width**: 1.5px
- **Size**: 20px, 24px, 32px (scale by 8px)
- **Library**: [Lucide Icons](https://lucide.dev/) or [Heroicons](https://heroicons.com/)
- **Color**: Inherit from parent, or subtle gray `#6B7280`

### Icon Usage

| Context | Icon | Size |
|---------|------|------|
| Buttons | Arrow right, Plus, Check | 20px |
| Cards | User, Calendar, MapPin | 24px |
| Hero sections | Stars, Moon | 48px |
| Tooltips | Info circle | 16px |

### Astrological Symbols

Use **Unicode symbols** (already implemented):
- Planets: ☉ ☽ ☿ ♀ ♂ ♃ ♄ ♅ ♆ ♇
- Signs: ♈ ♉ ♊ ♋ ♌ ♍ ♎ ♏ ♐ ♑ ♒ ♓
- Aspects: ☌ ☍ △ □ ⚹

**Font**: Use system fonts or embed "Astrological" font for consistency

---

## ♿ 9. Accessibility

### WCAG 2.1 AA Compliance

**Color Contrast**:
- Text on light background: Minimum 4.5:1
- Large text (18px+): Minimum 3:1
- UI components: Minimum 3:1

**Current Palette Compliance**:
- `#2B2B38` on `#FAFAFF`: ✅ 13.5:1 (AAA)
- `#4A5FC1` on white: ✅ 7.2:1 (AAA)
- `#6B7280` on white: ✅ 4.6:1 (AA)

**Keyboard Navigation**:
- All interactive elements have `:focus` states
- Tab order follows logical flow
- Skip links for screen readers
- Focus indicators: 3px solid `#4A5FC1`, 4px offset

**Screen Reader Support**:
- Semantic HTML (`<header>`, `<nav>`, `<main>`, `<article>`)
- ARIA labels for icons
- Alternative text for images
- Live regions for dynamic content

**Motion Preferences**:
```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## 🎯 10. Design Tokens (for Figma/Code)

### Complete Token List

```json
{
  "color": {
    "primary": "#4A5FC1",
    "secondary": "#C8A2C8",
    "accent": "#F4EDE2",
    "background": {
      "light": "#FAFAFF",
      "gradient": "linear-gradient(180deg, #FDFBFF 0%, #F3F6FF 100%)"
    },
    "text": {
      "primary": "#2B2B38",
      "secondary": "#6B7280",
      "muted": "#9CA3AF"
    },
    "border": {
      "default": "#D8DAE5",
      "hover": "#C8A2C8"
    },
    "semantic": {
      "success": "#10B981",
      "warning": "#F59E0B",
      "error": "#EF4444",
      "info": "#3B82F6"
    }
  },
  "typography": {
    "fontFamily": {
      "heading": "Playfair Display, serif",
      "body": "Inter, sans-serif",
      "mono": "Inter Tight, monospace"
    },
    "fontSize": {
      "xs": "12px",
      "sm": "13px",
      "base": "15px",
      "lg": "16px",
      "xl": "18px",
      "2xl": "22px",
      "3xl": "28px",
      "4xl": "38px"
    },
    "fontWeight": {
      "regular": 400,
      "medium": 500,
      "semibold": 600,
      "bold": 700
    },
    "lineHeight": {
      "tight": 1.2,
      "normal": 1.5,
      "relaxed": 1.6
    }
  },
  "spacing": {
    "xs": "4px",
    "sm": "8px",
    "md": "16px",
    "lg": "24px",
    "xl": "32px",
    "2xl": "48px",
    "3xl": "64px",
    "4xl": "96px"
  },
  "borderRadius": {
    "sm": "8px",
    "md": "12px",
    "lg": "16px",
    "xl": "20px",
    "2xl": "24px",
    "full": "9999px"
  },
  "shadow": {
    "sm": "0 2px 8px rgba(43, 43, 56, 0.04)",
    "md": "0 4px 16px rgba(43, 43, 56, 0.08)",
    "lg": "0 8px 24px rgba(43, 43, 56, 0.12)",
    "xl": "0 16px 48px rgba(43, 43, 56, 0.16)"
  }
}
```

---

## 🚀 Implementation Roadmap

### Phase 1: Foundation (Week 1–2)
- [ ] Set up Figma file with design tokens
- [ ] Create component library (buttons, inputs, cards)
- [ ] Define color system in Tailwind config
- [ ] Set up typography (import Google Fonts)

### Phase 2: Core Screens (Week 3–4)
- [ ] Redesign Login page
- [ ] Redesign Registration page
- [ ] Redesign Dashboard
- [ ] Implement new color palette

### Phase 3: Forms & Data (Week 5–6)
- [ ] Multi-step chart creation form
- [ ] Redesign "My Maps" grid
- [ ] Enhance chart detail page
- [ ] Add animations and transitions

### Phase 4: Polish (Week 7–8)
- [ ] Micro-interactions on all buttons/cards
- [ ] Loading states and skeletons
- [ ] Empty states with illustrations
- [ ] Accessibility audit
- [ ] Mobile optimization

---

## 📚 Resources

### Fonts
- [Playfair Display](https://fonts.google.com/specimen/Playfair+Display) — Google Fonts
- [Inter](https://fonts.google.com/specimen/Inter) — Google Fonts
- [Inter Tight](https://fonts.google.com/specimen/Inter+Tight) — Google Fonts

### Icons
- [Lucide Icons](https://lucide.dev/) — Modern, consistent icon set
- [Heroicons](https://heroicons.com/) — Tailwind's official icons
- [Unicode Astrological Symbols](https://www.unicode.org/charts/PDF/U2600.pdf) — For planets and signs

### Inspiration
- [Dribbble: Astrology UI](https://dribbble.com/search/astrology-app)
- [Behance: Mystical Design](https://www.behance.net/search/projects?search=mystical+ui)
- [Co-Star](https://www.costarastrology.com/) — Minimalist astrology app
- [Sanctuary](https://www.sanctuary.us/) — Premium astrology platform

### Tools
- [Figma](https://figma.com) — Design tool
- [Coolors](https://coolors.co/) — Color palette generator
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/) — Accessibility testing

---

## ✅ Design Checklist

Before shipping any new screen:

- [ ] Uses defined color palette (no random colors)
- [ ] Typography follows type scale
- [ ] Spacing uses 8px grid system
- [ ] Has proper hover/focus states
- [ ] Passes WCAG AA contrast requirements
- [ ] Tested on mobile viewport
- [ ] Animations respect `prefers-reduced-motion`
- [ ] All interactive elements have 44px+ touch targets
- [ ] Loading states are designed
- [ ] Empty states are designed
- [ ] Error states are designed

---

## 🎨 Quick Reference Card

```
┌─────────────────────────────────────────┐
│  ASTRO ESSENCE — DESIGN AT A GLANCE    │
├─────────────────────────────────────────┤
│                                         │
│  Colors:                                │
│  ● #4A5FC1  Primary (Indigo)           │
│  ● #C8A2C8  Secondary (Lavender)       │
│  ● #2B2B38  Text Dark                  │
│  ● #F4EDE2  Accent Ivory               │
│                                         │
│  Typography:                            │
│  ● Playfair Display — Headings         │
│  ● Inter — Body & UI                   │
│  ● Inter Tight — Numbers               │
│                                         │
│  Spacing:                               │
│  ● 8px base unit                       │
│  ● 24px card padding                   │
│  ● 48px section gaps                   │
│                                         │
│  Borders:                               │
│  ● 20px border radius (cards)          │
│  ● 1.5px border width                  │
│                                         │
│  Shadows:                               │
│  ● sm: 0 2px 8px rgba(43,43,56,0.04)  │
│  ● lg: 0 8px 24px rgba(43,43,56,0.12) │
│                                         │
└─────────────────────────────────────────┘
```

---

**Last Updated**: November 2025
**Version**: 1.0
**Maintained By**: Astro Development Team
