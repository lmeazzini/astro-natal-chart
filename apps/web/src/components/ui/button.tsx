import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"
import { motion } from "framer-motion"
import { buttonHover, buttonTap } from "@/config/animations"
import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap text-sm font-medium transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0",
  {
    variants: {
      variant: {
        // Primary: Indigo background with hover lift
        default:
          "bg-primary text-primary-foreground rounded-astro-sm shadow-sm hover:shadow-md hover:-translate-y-0.5 active:translate-y-0",
        // Secondary: Outline with hover background
        secondary:
          "border-2 border-primary bg-transparent text-primary rounded-astro-sm hover:bg-primary/5 hover:-translate-y-0.5 active:translate-y-0",
        // Subtle: Light background with hover
        subtle:
          "bg-muted text-foreground rounded-astro-sm hover:bg-muted/80 hover:-translate-y-0.5 active:translate-y-0",
        // Destructive: Red for errors
        destructive:
          "bg-destructive text-destructive-foreground rounded-astro-sm shadow-sm hover:bg-destructive/90 hover:-translate-y-0.5 active:translate-y-0",
        // Outline: Border with accent hover
        outline:
          "border border-input bg-background rounded-astro-sm shadow-sm hover:bg-accent hover:text-accent-foreground",
        // Ghost: Minimal styling
        ghost: "hover:bg-accent hover:text-accent-foreground rounded-astro-sm",
        // Link: Text only
        link: "text-primary underline-offset-4 hover:underline",
      },
      size: {
        default: "h-10 px-5 py-2.5",
        sm: "h-8 rounded-astro-sm px-3 text-xs",
        lg: "h-12 rounded-astro-md px-6 text-base",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    if (asChild) {
      return (
        <Slot
          className={cn(buttonVariants({ variant, size, className }))}
          ref={ref}
          {...props}
        />
      )
    }

    const {
      onDrag: _,
      onDragEnd: _end,
      onDragEnter: _enter,
      onDragExit: _exit,
      onDragLeave: _leave,
      onDragOver: _over,
      onDragStart: _start,
      onDrop: _drop,
      onAnimationStart: _animStart,
      onAnimationEnd: _animEnd,
      onAnimationIteration: _animIter,
      ...motionProps
    } = props;

    return (
      <motion.button
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        whileHover={props.disabled ? undefined : buttonHover}
        whileTap={props.disabled ? undefined : buttonTap}
        {...motionProps}
      />
    )
  }
)
Button.displayName = "Button"

export { Button, buttonVariants }
