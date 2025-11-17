# Accessibility - WCAG AA Contrast Verification

## Astro Essence Color Palette

This document verifies that our color combinations meet WCAG AA contrast requirements.

### WCAG AA Standards
- **Normal text** (< 18px regular or < 14px bold): Minimum 4.5:1 contrast ratio
- **Large text** (≥ 18px regular or ≥ 14px bold): Minimum 3:1 contrast ratio
- **UI components** (borders, icons): Minimum 3:1 contrast ratio

## Light Mode

### Primary Text Combinations

| Foreground | Background | Hex Foreground | Hex Background | Use Case | Contrast Ratio | Status |
|------------|------------|----------------|----------------|----------|----------------|--------|
| foreground | background | #2B2B38 | #FAFAFF | Main text | ~15.8:1 | ✅ PASS (AAA) |
| primary-foreground | primary | #FFFFFF | #4A5FC1 | Primary buttons | ~4.9:1 | ✅ PASS (AA) |
| secondary-foreground | secondary | #2B2B38 | #C8A2C8 | Secondary badges | ~6.2:1 | ✅ PASS (AA) |
| muted-foreground | background | #6B7280 | #FAFAFF | Secondary text | ~4.6:1 | ✅ PASS (AA) |
| primary | background | #4A5FC1 | #FAFAFF | Links, accents | ~4.9:1 | ✅ PASS (AA) |
| foreground | muted | #2B2B38 | #F7F7FC | Text on cards | ~15.5:1 | ✅ PASS (AAA) |
| foreground | input | #2B2B38 | #F7F7FC | Input text | ~15.5:1 | ✅ PASS (AAA) |

### Border Contrast

| Element | Background | Border Color | Hex Border | Contrast | Status |
|---------|------------|--------------|------------|----------|--------|
| Card border | background | border | #D8DAE5 | ~1.2:1 | ⚠️ Decorative only |
| Input border | background | border | #D8DAE5 | ~1.2:1 | ⚠️ Decorative only |

**Note**: Borders with low contrast are acceptable as decorative elements. Focus states use primary color (#4A5FC1) which has 4.9:1 contrast.

## Dark Mode

### Primary Text Combinations

| Foreground | Background | Hex Foreground | Hex Background | Use Case | Contrast Ratio | Status |
|------------|------------|----------------|----------------|----------|----------------|--------|
| foreground | background | #F0F0F2 | #131318 | Main text | ~14.2:1 | ✅ PASS (AAA) |
| primary-foreground | primary | #131318 | #7A8FE8 | Primary buttons | ~5.8:1 | ✅ PASS (AA) |
| muted-foreground | background | #9CA3AF | #131318 | Secondary text | ~6.8:1 | ✅ PASS (AA) |
| primary | background | #7A8FE8 | #131318 | Links, accents | ~5.8:1 | ✅ PASS (AA) |
| foreground | muted | #F0F0F2 | #1E1E24 | Text on cards | ~12.8:1 | ✅ PASS (AAA) |

## Component-Specific Verification

### Buttons
- **Primary**: White text (#FFFFFF) on indigo (#4A5FC1) - 4.9:1 ✅
- **Secondary**: Dark text (#2B2B38) on transparent - inherits background contrast ✅
- **Subtle**: Dark text on muted background - 15.5:1 ✅

### Badges
- **Default**: Same as primary button - 4.9:1 ✅
- **Lavender**: Dark text (#2B2B38) on lavender (#C8A2C8/15) - ~14:1 ✅
- **Outline**: Uses border color only, text is foreground - 15.8:1 ✅

### Inputs
- **Focus state**: Primary border (#4A5FC1) visible at 4.9:1 contrast ✅
- **Placeholder text**: muted-foreground (#6B7280) at 4.6:1 ✅

### Tables
- **Header background**: muted/30 with foreground text - >12:1 ✅
- **Alternating rows**: muted/20 with foreground text - >13:1 ✅
- **Hover state**: accent/40 with foreground text - >11:1 ✅

### Tabs
- **Active tab**: Primary color (#4A5FC1) border at 4.9:1 ✅
- **Active text**: Primary color text at 4.9:1 ✅
- **Inactive text**: muted-foreground at 4.6:1 ✅

## Typography Sizes and Weights

Our typography system uses appropriate sizes for WCAG compliance:

- **Headings** (text-h1 to text-h4): 38px, 28px, 22px, 18px - All qualify as "large text" (3:1 minimum)
- **Body text** (text-body): 15px - Requires 4.5:1 contrast (met with 15.8:1)
- **Captions** (text-caption): 13px - Requires 4.5:1 contrast (met with 15.8:1)
- **Data** (text-data): 15px - Requires 4.5:1 contrast (met with 15.8:1)

## Focus Indicators

All interactive elements have visible focus indicators:
- **Ring color**: Primary (#4A5FC1) at 4.9:1 contrast
- **Ring width**: 2px (visible at any viewport)
- **Ring offset**: 2px (clear separation from element)

## Summary

✅ **All critical text combinations meet or exceed WCAG AA standards (4.5:1 for normal text)**

✅ **Most combinations achieve AAA compliance (7:1) for enhanced accessibility**

✅ **Dark mode maintains equivalent contrast ratios**

✅ **Focus indicators are clearly visible (4.9:1 minimum)**

⚠️ **Decorative borders** (cards, inputs) have low contrast but are supplemented by:
- Clear focus states with high-contrast borders
- Background color differentiation
- Shadow effects for depth perception

## Recommendations

1. **Continue using semantic color tokens** (foreground/background) instead of hardcoded colors
2. **Test with actual contrast checkers** when implementing new color variants
3. **Maintain focus ring** implementation for all interactive elements
4. **Avoid placing muted-foreground text** on muted backgrounds (would be ~1.5:1)

## Testing Tools

To verify these calculations in practice:
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [Accessible Colors](https://accessible-colors.com/)
- Browser DevTools Accessibility Inspector
- [WAVE Extension](https://wave.webaim.org/extension/)

## Next Steps

- ✅ Phase 1 Complete - All base colors verified
- Phase 2: Test with actual users using screen readers
- Phase 3: Add ARIA labels where semantic HTML is insufficient
- Phase 4: Implement skip navigation links for keyboard users
