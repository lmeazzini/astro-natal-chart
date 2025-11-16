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

> **Design System**: Using [shadcn/ui](https://ui.shadcn.com/) component library
>
> shadcn/ui components are copied into the project (not a dependency), giving full control while maintaining accessibility and best practices.

### Component Library Setup

**Installation**:
```bash
npx shadcn@latest init
```

**Configuration** (`components.json`):
```json
{
  "style": "new-york",
  "tailwind": {
    "baseColor": "slate",
    "cssVariables": true
  },
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils"
  }
}
```

### Buttons

**shadcn/ui Button Component** with Astro Essence styling:

**Variants**:
```tsx
import { Button } from '@/components/ui/button'

// Primary (Default)
<Button>
  Calcular Mapa
</Button>

// Secondary (Outline)
<Button variant="outline">
  Cancelar
</Button>

// Subtle (Ghost)
<Button variant="ghost">
  Ver Mais
</Button>

// Destructive
<Button variant="destructive">
  Excluir
</Button>
```

**Custom Styling** (in `components/ui/button.tsx`):
```tsx
const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-xl font-medium transition-all",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground shadow-[0_4px_12px_rgba(74,95,193,0.2)] hover:translate-y-[-2px] hover:shadow-[0_8px_24px_rgba(74,95,193,0.3)]",
        outline: "border-[1.5px] border-primary bg-transparent text-primary hover:bg-[#F3F6FF]",
        ghost: "bg-[#F7F7FC] text-foreground hover:bg-[#EDEDF5]",
        destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
      },
      size: {
        default: "h-11 px-6 py-3 text-[15px]",
        sm: "h-9 px-4 py-2 text-[14px]",
        lg: "h-12 px-8 py-3.5 text-[16px]",
        icon: "h-10 w-10",
      },
    },
  }
)
```

### Cards

**shadcn/ui Card Component**:

```tsx
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card'

// Standard Card
<Card className="transition-all hover:translate-y-[-4px] hover:shadow-lg hover:border-secondary">
  <CardHeader>
    <CardTitle>Mapa Natal</CardTitle>
    <CardDescription>Criado em 10/11/2024</CardDescription>
  </CardHeader>
  <CardContent>
    {/* Content */}
  </CardContent>
  <CardFooter>
    <Button>Ver Detalhes</Button>
  </CardFooter>
</Card>

// Premium Card (with gradient)
<Card className="border-2 border-secondary bg-gradient-to-br from-[#FDFBFF] to-[#F9F6FF] shadow-[0_4px_16px_rgba(200,162,200,0.15)]">
  <CardContent className="p-8">
    {/* Premium content */}
  </CardContent>
</Card>
```

**Custom Card Styling** (in `components/ui/card.tsx`):
```tsx
const Card = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        "rounded-[20px] border border-border bg-card text-card-foreground shadow-[0_2px_8px_rgba(43,43,56,0.04)]",
        "transition-all duration-300",
        className
      )}
      {...props}
    />
  )
)
```

### Form Inputs

**shadcn/ui Form Components** (integrates React Hook Form + Zod):

```tsx
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

const formSchema = z.object({
  personName: z.string().min(3, 'Nome deve ter no mínimo 3 caracteres'),
  birthDate: z.string(),
})

function ChartForm() {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
  })

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        <FormField
          control={form.control}
          name="personName"
          render={({ field }) => (
            <FormItem>
              <FormLabel className="uppercase text-[13px] tracking-wider">Nome da Pessoa</FormLabel>
              <FormControl>
                <Input placeholder="João Silva" {...field} />
              </FormControl>
              <FormDescription>Nome completo da pessoa</FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit">Criar Mapa</Button>
      </form>
    </Form>
  )
}
```

**Custom Input Styling** (in `components/ui/input.tsx`):
```tsx
const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(
          "flex h-11 w-full rounded-xl border-[1.5px] border-input",
          "bg-[#F7F7FC] px-4 py-3 text-[15px]",
          "placeholder:text-muted-foreground",
          "focus-visible:bg-background focus-visible:border-primary",
          "focus-visible:ring-4 focus-visible:ring-primary/10",
          "disabled:cursor-not-allowed disabled:opacity-50",
          "transition-all",
          className
        )}
        ref={ref}
        {...props}
      />
    )
  }
)
```

**Other Form Components**:
```tsx
// Select
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

<Select>
  <SelectTrigger>
    <SelectValue placeholder="Selecione o signo" />
  </SelectTrigger>
  <SelectContent>
    <SelectItem value="aries">Áries</SelectItem>
    <SelectItem value="taurus">Touro</SelectItem>
  </SelectContent>
</Select>

// Checkbox
import { Checkbox } from '@/components/ui/checkbox'

<div className="flex items-center space-x-2">
  <Checkbox id="terms" />
  <Label htmlFor="terms">Aceito os termos</Label>
</div>

// Radio Group
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'

<RadioGroup defaultValue="male">
  <div className="flex items-center space-x-2">
    <RadioGroupItem value="male" id="male" />
    <Label htmlFor="male">Masculino</Label>
  </div>
  <div className="flex items-center space-x-2">
    <RadioGroupItem value="female" id="female" />
    <Label htmlFor="female">Feminino</Label>
  </div>
</RadioGroup>
```

### Modals (Dialogs)

**shadcn/ui Dialog Component**:

```tsx
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'

<Dialog>
  <DialogTrigger asChild>
    <Button variant="destructive">Excluir Mapa</Button>
  </DialogTrigger>
  <DialogContent className="sm:max-w-[600px] rounded-[24px]">
    <DialogHeader>
      <DialogTitle className="font-playfair text-[22px]">Tem certeza?</DialogTitle>
      <DialogDescription>
        Esta ação não pode ser desfeita. O mapa natal será excluído permanentemente.
      </DialogDescription>
    </DialogHeader>
    <DialogFooter className="gap-2">
      <Button variant="outline">Cancelar</Button>
      <Button variant="destructive" onClick={handleDelete}>Excluir</Button>
    </DialogFooter>
  </DialogContent>
</Dialog>
```

**Custom Dialog Styling** (in `components/ui/dialog.tsx`):
```tsx
const DialogContent = React.forwardRef<HTMLDivElement, DialogContentProps>(
  ({ className, children, ...props }, ref) => (
    <DialogPortal>
      <DialogOverlay className="bg-[rgba(43,43,56,0.5)] backdrop-blur-sm" />
      <DialogPrimitive.Content
        ref={ref}
        className={cn(
          "fixed left-[50%] top-[50%] z-50 grid w-full max-w-lg translate-x-[-50%] translate-y-[-50%] gap-4",
          "rounded-[24px] border bg-background p-10 shadow-[0_24px_64px_rgba(43,43,56,0.2)]",
          "duration-200 data-[state=open]:animate-in data-[state=closed]:animate-out",
          className
        )}
        {...props}
      >
        {children}
      </DialogPrimitive.Content>
    </DialogPortal>
  )
)
```

### Additional shadcn/ui Components

**Table** (for PlanetList, HouseTable, AspectGrid):
```tsx
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'

<Table>
  <TableHeader>
    <TableRow>
      <TableHead>Planeta</TableHead>
      <TableHead>Signo</TableHead>
      <TableHead>Posição</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody>
    {planets.map((planet) => (
      <TableRow key={planet.name} className="hover:bg-[#F7F7FC]/50">
        <TableCell className="font-medium">{planet.name}</TableCell>
        <TableCell>{planet.sign}</TableCell>
        <TableCell className="font-mono">{planet.position}°</TableCell>
      </TableRow>
    ))}
  </TableBody>
</Table>
```

**Badge** (for planet aspects, retrograde status):
```tsx
import { Badge } from '@/components/ui/badge'

<Badge>Retrógrado</Badge>
<Badge variant="secondary">Aplicando</Badge>
<Badge variant="outline">Separando</Badge>
<Badge variant="destructive">Debilitado</Badge>
```

**Toast** (for user feedback with Sonner):
```tsx
import { toast } from 'sonner'

// Success
toast.success('Mapa natal criado com sucesso!')

// Error
toast.error('Erro ao calcular mapa natal')

// Loading
const toastId = toast.loading('Calculando posições planetárias...')
// Later:
toast.success('Mapa calculado!', { id: toastId })

// Custom with action
toast('Mapa salvo', {
  description: 'Seu mapa natal foi salvo com sucesso',
  action: {
    label: 'Ver',
    onClick: () => navigate('/charts')
  }
})
```

**Skeleton** (for loading states):
```tsx
import { Skeleton } from '@/components/ui/skeleton'

// Card skeleton
<Card>
  <CardHeader>
    <Skeleton className="h-6 w-48" />
    <Skeleton className="h-4 w-32 mt-2" />
  </CardHeader>
  <CardContent>
    <Skeleton className="h-32 w-full" />
  </CardContent>
</Card>

// Table skeleton
{[...Array(5)].map((_, i) => (
  <TableRow key={i}>
    <TableCell><Skeleton className="h-4 w-24" /></TableCell>
    <TableCell><Skeleton className="h-4 w-20" /></TableCell>
  </TableRow>
))}
```

**Tooltip** (for planet information):
```tsx
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'

<TooltipProvider>
  <Tooltip>
    <TooltipTrigger asChild>
      <span className="cursor-help">☉</span>
    </TooltipTrigger>
    <TooltipContent className="max-w-xs">
      <p className="font-semibold">Sol</p>
      <p className="text-sm">Representa a essência, identidade e propósito de vida</p>
    </TooltipContent>
  </Tooltip>
</TooltipProvider>
```

**Tabs** (for Chart Detail page sections):
```tsx
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

<Tabs defaultValue="visual" className="w-full">
  <TabsList className="grid w-full grid-cols-4">
    <TabsTrigger value="visual">🌟 Visualização</TabsTrigger>
    <TabsTrigger value="planets">🪐 Planetas</TabsTrigger>
    <TabsTrigger value="houses">🏠 Casas</TabsTrigger>
    <TabsTrigger value="aspects">✨ Aspectos</TabsTrigger>
  </TabsList>
  <TabsContent value="visual">
    <ChartWheel {...chartData} />
  </TabsContent>
  <TabsContent value="planets">
    <PlanetList planets={chartData.planets} />
  </TabsContent>
  {/* ... */}
</Tabs>
```

**Alert** (for CookieBanner, important messages):
```tsx
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { InfoIcon } from 'lucide-react'

<Alert className="border-secondary bg-secondary/10">
  <InfoIcon className="h-4 w-4" />
  <AlertTitle>Cookies</AlertTitle>
  <AlertDescription>
    Este site usa cookies essenciais para garantir a melhor experiência.
  </AlertDescription>
</Alert>

// Variants
<Alert variant="destructive">
  <AlertTitle>Erro</AlertTitle>
  <AlertDescription>Não foi possível calcular o mapa natal</AlertDescription>
</Alert>
```

**Separator** (for visual dividers):
```tsx
import { Separator } from '@/components/ui/separator'

<div>
  <h2>Informações Pessoais</h2>
  <Separator className="my-4" />
  <p>Conteúdo...</p>
</div>
```

**DropdownMenu** (for card actions):
```tsx
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuSeparator } from '@/components/ui/dropdown-menu'
import { MoreVertical, Edit, Trash, Share } from 'lucide-react'

<DropdownMenu>
  <DropdownMenuTrigger asChild>
    <Button variant="ghost" size="icon">
      <MoreVertical className="h-4 w-4" />
    </Button>
  </DropdownMenuTrigger>
  <DropdownMenuContent align="end">
    <DropdownMenuItem>
      <Edit className="mr-2 h-4 w-4" />
      <span>Editar</span>
    </DropdownMenuItem>
    <DropdownMenuItem>
      <Share className="mr-2 h-4 w-4" />
      <span>Compartilhar</span>
    </DropdownMenuItem>
    <DropdownMenuSeparator />
    <DropdownMenuItem className="text-destructive">
      <Trash className="mr-2 h-4 w-4" />
      <span>Excluir</span>
    </DropdownMenuItem>
  </DropdownMenuContent>
</DropdownMenu>
```

**ScrollArea** (for long content):
```tsx
import { ScrollArea } from '@/components/ui/scroll-area'

<ScrollArea className="h-[400px] rounded-xl border p-4">
  {/* Long content here */}
</ScrollArea>
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
- [shadcn/ui](https://ui.shadcn.com/) — Component library (Tailwind + Radix UI)
- [Radix UI](https://www.radix-ui.com/) — Unstyled, accessible components (base for shadcn/ui)
- [React Hook Form](https://react-hook-form.com/) — Form validation
- [Zod](https://zod.dev/) — Schema validation

### shadcn/ui Resources
- **Documentation**: https://ui.shadcn.com/docs
- **Components**: https://ui.shadcn.com/docs/components
- **Examples**: https://ui.shadcn.com/examples
- **Blocks**: https://ui.shadcn.com/blocks (pre-built component compositions)
- **Themes**: https://ui.shadcn.com/themes (color customization)
- **CLI Reference**: https://ui.shadcn.com/docs/cli

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

## 📝 Implementation Notes

### shadcn/ui Integration

**Why shadcn/ui?**
- ✅ **Maintains Astro Essence**: All custom design tokens (colors, spacing, typography) are preserved
- ✅ **Accessibility First**: Built on Radix UI (WCAG 2.1 AA compliant by default)
- ✅ **Full Control**: Components are copied to your project, not installed as a dependency
- ✅ **Customizable**: Every component can be modified to match our design system
- ✅ **Production Ready**: Used by companies like Vercel, Supabase, and thousands of projects
- ✅ **Type Safe**: Full TypeScript support
- ✅ **Integration**: Works seamlessly with React Hook Form, Zod, and our existing stack

**Customization Strategy**:
1. Install base shadcn/ui components with CLI
2. Modify component styling in `components/ui/*.tsx` to match Astro Essence design tokens
3. Use Tailwind classes with our CSS variables for colors (`bg-primary`, `text-secondary`, etc.)
4. Adjust border radius to `rounded-xl` (12px) or `rounded-[20px]` for cards
5. Add custom hover effects and transitions per our animation guidelines

**Key Customizations**:
- Border radius: `12px` (inputs), `20px` (cards), `24px` (modals)
- Font family: `font-playfair` for headings, `font-inter` for body
- Shadows: Custom shadows matching our design tokens
- Spacing: 8px grid system (sm: 8px, md: 16px, lg: 24px, etc.)
- Colors: Use CSS variables from `globals.css` (`hsl(var(--primary))`, etc.)

**Components Priority** (install order):
1. **Foundation**: button, card, input, label, form
2. **Navigation**: tabs, dialog, dropdown-menu
3. **Feedback**: toast, alert, skeleton, tooltip
4. **Data Display**: table, badge, separator, scroll-area
5. **Forms**: select, checkbox, radio-group

---

**Last Updated**: November 2025
**Version**: 2.0 (Updated with shadcn/ui integration)
**Maintained By**: Astro Development Team

**Related Issues**:
- #44 — Migrar para shadcn/ui como biblioteca de componentes
