import * as React from "react"
import { motion } from "framer-motion"
import { cardHover, fadeInUp } from "@/config/animations"
import { cn } from "@/lib/utils"

const Card = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => {
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
    <motion.div
      ref={ref}
      className={cn(
        "rounded-astro-lg border bg-card text-card-foreground shadow-sm",
        className
      )}
      initial="hidden"
      animate="visible"
      variants={fadeInUp}
      whileHover={cardHover}
      transition={{ duration: 0.3 }}
      {...motionProps}
    />
  );
})
Card.displayName = "Card"

const CardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex flex-col space-y-2 p-astro-lg", className)}
    {...props}
  />
))
CardHeader.displayName = "CardHeader"

const CardTitle = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("font-semibold leading-none tracking-tight", className)}
    {...props}
  />
))
CardTitle.displayName = "CardTitle"

const CardDescription = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("text-sm text-muted-foreground", className)}
    {...props}
  />
))
CardDescription.displayName = "CardDescription"

const CardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("p-astro-lg pt-0", className)} {...props} />
))
CardContent.displayName = "CardContent"

const CardFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex items-center p-astro-lg pt-0", className)}
    {...props}
  />
))
CardFooter.displayName = "CardFooter"

export { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent }
