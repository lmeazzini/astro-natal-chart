import * as React from "react"
import { Check } from "lucide-react"

import { cn } from "@/lib/utils"

interface ProgressIndicatorProps extends React.HTMLAttributes<HTMLDivElement> {
  step: number
  completed?: boolean
  active?: boolean
}

const ProgressIndicator = React.forwardRef<HTMLDivElement, ProgressIndicatorProps>(
  ({ className, step, completed = false, active = false, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          "relative flex h-12 w-12 items-center justify-center rounded-full border-2 text-sm font-semibold transition-all duration-300",
          {
            "border-primary bg-primary text-primary-foreground shadow-md": completed,
            "border-primary bg-background text-primary ring-4 ring-primary/20": active && !completed,
            "border-border bg-background text-muted-foreground": !active && !completed,
          },
          className
        )}
        {...props}
      >
        {completed ? (
          <Check className="h-5 w-5" strokeWidth={3} />
        ) : (
          <span>{step}</span>
        )}
      </div>
    )
  }
)
ProgressIndicator.displayName = "ProgressIndicator"

export { ProgressIndicator, type ProgressIndicatorProps }
