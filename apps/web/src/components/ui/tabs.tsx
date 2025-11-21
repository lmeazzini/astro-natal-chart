import * as React from "react"
import * as TabsPrimitive from "@radix-ui/react-tabs"
import { motion, AnimatePresence } from "framer-motion"
import { cn } from "@/lib/utils"
import { tabContent, spring } from "@/config/animations"

const Tabs = TabsPrimitive.Root

const TabsList = React.forwardRef<
  React.ElementRef<typeof TabsPrimitive.List>,
  React.ComponentPropsWithoutRef<typeof TabsPrimitive.List>
>(({ className, children, ...props }, ref) => (
  <TabsPrimitive.List
    ref={ref}
    className={cn(
      "inline-flex h-auto items-center gap-2 border-b border-border text-muted-foreground",
      className
    )}
    {...props}
  >
    {children}
  </TabsPrimitive.List>
))
TabsList.displayName = TabsPrimitive.List.displayName

const TabsTrigger = React.forwardRef<
  React.ElementRef<typeof TabsPrimitive.Trigger>,
  React.ComponentPropsWithoutRef<typeof TabsPrimitive.Trigger>
>(({ className, children, ...props }, ref) => {
  const [isActive, setIsActive] = React.useState(false);
  const dataState = props['data-state' as keyof typeof props] as string | undefined;

  return (
    <TabsPrimitive.Trigger
      ref={ref}
      className={cn(
        "relative inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-t-astro-sm px-4 py-3 text-base font-medium transition-all duration-200 hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
        isActive && "text-primary font-semibold",
        className
      )}
      onFocus={() => setIsActive(true)}
      onBlur={() => setIsActive(false)}
      {...props}
    >
      {children}
      {/* Animated underline */}
      <AnimatePresence>
        {dataState === 'active' && (
          <motion.div
            className="absolute bottom-0 left-0 right-0 h-[3px] bg-primary"
            initial={{ scaleX: 0, opacity: 0 }}
            animate={{ scaleX: 1, opacity: 1 }}
            exit={{ scaleX: 0, opacity: 0 }}
            transition={spring.default}
            style={{ originX: 0.5 }}
          />
        )}
      </AnimatePresence>
    </TabsPrimitive.Trigger>
  );
})
TabsTrigger.displayName = TabsPrimitive.Trigger.displayName

// Animated TabsContent with motion
const TabsContent = React.forwardRef<
  React.ElementRef<typeof TabsPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof TabsPrimitive.Content>
>(({ className, children, ...props }, ref) => (
  <TabsPrimitive.Content
    ref={ref}
    className={cn(
      "mt-astro-lg ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
      className
    )}
    {...props}
    asChild
  >
    <motion.div
      initial="hidden"
      animate="visible"
      exit="exit"
      variants={tabContent}
    >
      {children}
    </motion.div>
  </TabsPrimitive.Content>
))
TabsContent.displayName = TabsPrimitive.Content.displayName

export { Tabs, TabsList, TabsTrigger, TabsContent }
