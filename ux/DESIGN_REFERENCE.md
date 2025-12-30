# Design Reference — "Midnight & Paper"

> A sophisticated, conversion-focused design system for traditional astrology

## Vision

Create a design that is:

- **Elegant & Timeless** — Deep midnight blue, warm gold accents, cream paper backgrounds
- **Trustworthy & Premium** — Clean layouts, generous spacing, focus on readability
- **Conversion-Focused** — Clear CTAs, compelling hero sections, social proof
- **Mature** — Targeting 30–45 demographic with sophistication
- **Historically Grounded** — Design that evokes ancient wisdom and scholarly tradition

---

## 1. Color Palette — "Midnight & Paper"

### Light Mode (Paper Theme)

| Purpose | CSS Variable | HSL Value | Description |
|---------|-------------|-----------|-------------|
| **Background** | `--background` | `40 20% 98%` | Deep cream/paper |
| **Foreground** | `--foreground` | `222 47% 11%` | Deep midnight blue/ink |
| **Card** | `--card` | `0 0% 100%` | Pure white |
| **Primary** | `--primary` | `222 47% 15%` | Deep cosmic blue |
| **Primary Foreground** | `--primary-foreground` | `43 74% 85%` | Soft gold text on primary |
| **Secondary** | `--secondary` | `43 40% 90%` | Stardust gold (muted) |
| **Muted** | `--muted` | `220 20% 94%` | Soft grey-blue |
| **Muted Foreground** | `--muted-foreground` | `220 20% 40%` | Grey text |
| **Accent** | `--accent` | `43 74% 66%` | Gold highlight |
| **Border** | `--border` | `220 13% 91%` | Subtle borders |
| **Destructive** | `--destructive` | `0 84% 60%` | Error red |

### Dark Mode (Deep Cosmos Theme)

| Purpose | CSS Variable | HSL Value | Description |
|---------|-------------|-----------|-------------|
| **Background** | `--background` | `222 47% 8%` | Deep space blue |
| **Foreground** | `--foreground` | `43 20% 90%` | Warm cream text |
| **Card** | `--card` | `222 47% 10%` | Slightly lighter blue |
| **Primary** | `--primary` | `43 74% 66%` | Gold |
| **Primary Foreground** | `--primary-foreground` | `222 47% 10%` | Dark blue text |
| **Secondary** | `--secondary` | `222 30% 20%` | Muted blue |
| **Muted** | `--muted` | `222 30% 15%` | Dark muted |
| **Accent** | `--accent` | `222 30% 20%` | Blue accent |
| **Accent Foreground** | `--accent-foreground` | `43 74% 66%` | Gold text |
| **Border** | `--border` | `222 30% 20%` | Subtle dark borders |

### Planet Colors (Chart Visualization)

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

---

## 2. Typography

### Font Families

**Display/Headings**: System serif stack or Playfair Display
- Used for H1-H3, hero titles, emotional moments
- Weights: Semibold (600)

**Body Text**: System sans-serif stack (Inter fallback)
- Used for body copy, UI elements, forms
- Weights: Regular (400), Medium (500), Semibold (600)

**Monospace**: System monospace
- Used for astronomical data, degrees, coordinates
- Tabular numbers enabled

### Type Scale (Tailwind Classes)

| Element | Class | Size | Usage |
|---------|-------|------|-------|
| **H1** | `text-h1` | 38px | Page titles |
| **H2** | `text-h2` | 28px | Section titles |
| **H3** | `text-h3` | 22px | Subsections |
| **H4** | `text-h4` | 18px | Card titles |
| **Body** | `text-body` | 15px | Default body text |
| **Caption** | `text-caption` | 13px | Labels, metadata |
| **Data** | `text-data` | 15px | Numbers, positions |

### Typography Utilities (globals.css)

```css
.text-h1 {
  @apply font-display text-[38px] font-semibold leading-tight;
}

.text-h2 {
  @apply font-display text-[28px] font-semibold leading-tight;
}

.text-h3 {
  @apply font-display text-[22px] font-semibold leading-snug;
}

.text-h4 {
  @apply font-body text-[18px] font-semibold leading-snug;
}

.text-body {
  @apply font-body text-[15px] font-normal leading-relaxed;
}

.text-caption {
  @apply font-body text-[13px] font-medium leading-normal;
}

.text-data {
  @apply font-mono text-[15px] font-medium leading-normal tabular-nums;
}
```

---

## 3. Spacing & Layout

### Spacing Scale (8px base)

| Token | Value | Usage |
|-------|-------|-------|
| `xs` | 4px | Tight spacing, icon gaps |
| `sm` | 8px | Small gaps, inline elements |
| `md` | 16px | Default spacing |
| `lg` | 24px | Section spacing, card padding |
| `xl` | 32px | Large section gaps |
| `2xl` | 48px | Major sections |
| `3xl` | 64px | Page-level spacing |
| `4xl` | 96px | Hero sections |

### Container Widths

- **Max Width**: 1440px (`max-w-7xl`)
- **Content Width**: 1200px
- **Reading Width**: 720px
- **Form Width**: 480px

---

## 4. UI Components

> Using **shadcn/ui** component library with Midnight & Paper customizations

### Buttons

```tsx
// Primary (gold accent)
<Button className="bg-accent text-accent-foreground hover:bg-accent/90">
  Create Chart
</Button>

// Ghost (transparent)
<Button variant="ghost" className="text-primary-foreground hover:bg-primary-foreground/10">
  Login
</Button>

// Outline
<Button variant="outline">
  Cancel
</Button>
```

### Cards

```tsx
<Card className="bg-card border-border rounded-2xl shadow-lg">
  <CardHeader>
    <CardTitle className="font-serif">Chart Title</CardTitle>
  </CardHeader>
  <CardContent>
    {/* Content */}
  </CardContent>
</Card>

// Feature card with gradient
<Card className="bg-gradient-to-br from-indigo-500/10 to-purple-500/10 border-indigo-500/20">
  {/* Premium content */}
</Card>
```

### Form Inputs

- Background: `bg-muted` (soft grey-blue)
- Border radius: `rounded-xl` (12px)
- Focus: `ring-2 ring-primary ring-offset-2`

---

## 5. Landing Page Structure

### Navigation (Sticky)

```tsx
<nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
  scrolled
    ? 'bg-primary/95 backdrop-blur-md border-b border-primary-foreground/20 shadow-lg'
    : 'bg-transparent'
}`}>
```

**Elements:**
- Logo (left)
- Navigation links: Blog, Techniques, Pricing (center, desktop only)
- Language selector, Theme toggle, Login, Sign Up (right)

### Hero Section

**Background:** Primary color with celestial map overlay
**Content:**
- Badge: "Rediscover Ancient Wisdom"
- H1: "Traditional Astrology for the Modern World" (serif, italicized highlight)
- Subtitle: Value proposition
- CTA buttons: Primary (gold) + Secondary (outline)

### Features Section

**6 feature cards** in 3-column grid:
1. Essential Dignities
2. Sect (Day/Night)
3. Arabic Parts
4. Temperament
5. Classical Reasoning
6. Life Cycles

### "Not Guesswork" Section

Split layout:
- Left: 3-step explanation with numbered circles
- Right: Animated chart visualization

### Philosophy Section

Quote block + 2 philosophy cards:
- "Map, Not Territory"
- "Character is Destiny"

### CTA Section

- GDPR badge
- Strong headline
- Social proof
- Primary CTA button

### Footer

3-column grid:
- Brand + tagline
- Legal links (Terms, Privacy, Cookies)
- Access links (Login, Register, Blog)

---

## 6. Animations

### Timing Functions

```css
--ease-smooth: cubic-bezier(0.4, 0, 0.2, 1);
--ease-out: cubic-bezier(0, 0, 0.2, 1);
```

### Standard Transitions

| Element | Property | Duration |
|---------|----------|----------|
| Buttons | all | 200ms |
| Cards | all | 300ms |
| Navbar | all | 300ms |
| Page elements | opacity, transform | 800ms |

### Keyframes (globals.css)

```css
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
```

### Framer Motion (Landing Page)

```tsx
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.8, ease: 'easeOut' }}
>
```

---

## 7. Responsive Design

### Breakpoints

- **Mobile**: `< 640px` (sm)
- **Tablet**: `640px - 1024px` (md)
- **Desktop**: `> 1024px` (lg)

### Mobile Considerations

- Navigation links hidden on mobile (`hidden md:flex`)
- Touch targets: 44px minimum
- Stack layouts on mobile
- Full-width buttons on mobile

---

## 8. Accessibility

### Focus States

```css
*:focus-visible {
  @apply outline-none ring-2 ring-primary ring-offset-2 ring-offset-background;
}
```

### Reduced Motion

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

### Color Contrast

All text colors meet WCAG 2.1 AA requirements:
- Primary text on background: > 4.5:1
- Muted text: > 4.5:1

---

## 9. Design Tokens (CSS Variables)

Located in `apps/web/src/styles/globals.css`:

```css
:root {
  /* Light Mode - "Midnight & Paper" */
  --background: 40 20% 98%;
  --foreground: 222 47% 11%;
  --card: 0 0% 100%;
  --card-foreground: 222 47% 11%;
  --primary: 222 47% 15%;
  --primary-foreground: 43 74% 85%;
  --secondary: 43 40% 90%;
  --secondary-foreground: 222 47% 11%;
  --muted: 220 20% 94%;
  --muted-foreground: 220 20% 40%;
  --accent: 43 74% 66%;
  --accent-foreground: 222 47% 11%;
  --border: 220 13% 91%;
  --input: 220 13% 91%;
  --ring: 222 47% 15%;
  --radius: 0.5rem;
}

.dark {
  /* Dark Mode - "Deep Cosmos" */
  --background: 222 47% 8%;
  --foreground: 43 20% 90%;
  --card: 222 47% 10%;
  --primary: 43 74% 66%;
  --primary-foreground: 222 47% 10%;
  --secondary: 222 30% 20%;
  --muted: 222 30% 15%;
  --accent: 222 30% 20%;
  --accent-foreground: 43 74% 66%;
  --border: 222 30% 20%;
  --ring: 43 74% 66%;
}
```

---

## 10. Quick Reference Card

```
┌─────────────────────────────────────────┐
│  MIDNIGHT & PAPER — DESIGN AT A GLANCE  │
├─────────────────────────────────────────┤
│                                         │
│  Light Mode:                            │
│  ● Background: Cream (#FAF9F6)          │
│  ● Primary: Midnight Blue (#1a1f36)     │
│  ● Accent: Gold (#d4a84b)               │
│  ● Text: Deep Ink (#1a1f36)             │
│                                         │
│  Dark Mode:                             │
│  ● Background: Deep Space (#121729)     │
│  ● Primary: Gold (#d4a84b)              │
│  ● Text: Warm Cream (#e8e0d0)           │
│                                         │
│  Typography:                            │
│  ● Headings: Serif (Playfair Display)   │
│  ● Body: Sans-serif (Inter)             │
│  ● Data: Monospace                      │
│                                         │
│  Spacing:                               │
│  ● 8px base unit                        │
│  ● 24px card padding                    │
│  ● 48px section gaps                    │
│                                         │
│  Border Radius:                         │
│  ● Buttons: rounded-full (pills)        │
│  ● Cards: rounded-2xl (16px)            │
│  ● Inputs: rounded-xl (12px)            │
│                                         │
│  Key Elements:                          │
│  ● Sticky navbar with scroll effect     │
│  ● Gold accent CTAs                     │
│  ● Framer Motion animations             │
│  ● Celestial background imagery         │
│                                         │
└─────────────────────────────────────────┘
```

---

## Design Checklist

Before shipping any new screen:

- [ ] Uses "Midnight & Paper" color palette
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

**Last Updated**: December 2024
**Version**: 3.0 — "Midnight & Paper" Theme
**Maintained By**: Astro Development Team
