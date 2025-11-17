import * as React from "react"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import { getPlanetSymbol, getSignSymbol } from "@/utils/astro"

interface BigThreeBadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  sunSign: string
  moonSign: string
  risingSign: string
  variant?: "horizontal" | "vertical"
}

const BigThreeBadge = React.forwardRef<HTMLDivElement, BigThreeBadgeProps>(
  ({ className, sunSign, moonSign, risingSign, variant = "horizontal", ...props }, ref) => {
    const items = [
      { label: "Sun", sign: sunSign, symbol: getPlanetSymbol("Sun") },
      { label: "Moon", sign: moonSign, symbol: getPlanetSymbol("Moon") },
      { label: "Rising", sign: risingSign, symbol: "ASC" },
    ]

    return (
      <div
        ref={ref}
        className={cn(
          "flex gap-2",
          {
            "flex-row flex-wrap": variant === "horizontal",
            "flex-col": variant === "vertical",
          },
          className
        )}
        {...props}
      >
        {items.map((item) => (
          <Badge key={item.label} variant="lavender" className="text-[13px]">
            <span className="opacity-70">{item.symbol}</span>
            <span className="font-semibold">{item.label}:</span>
            <span>{getSignSymbol(item.sign)}</span>
            <span>{item.sign}</span>
          </Badge>
        ))}
      </div>
    )
  }
)
BigThreeBadge.displayName = "BigThreeBadge"

export { BigThreeBadge, type BigThreeBadgeProps }
