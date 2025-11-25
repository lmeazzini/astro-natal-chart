import * as React from 'react';
import { LucideIcon } from 'lucide-react';

import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';

interface EmptyStateProps extends React.HTMLAttributes<HTMLDivElement> {
  icon?: LucideIcon;
  title: string;
  description?: string;
  action?: {
    label: string;
    onClick: () => void;
  };
}

const EmptyState = React.forwardRef<HTMLDivElement, EmptyStateProps>(
  ({ className, icon: Icon, title, description, action, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          'flex flex-col items-center justify-center py-astro-3xl px-astro-lg text-center',
          className
        )}
        {...props}
      >
        {Icon && (
          <div className="mb-astro-lg rounded-full bg-muted/50 p-astro-lg">
            <Icon className="h-12 w-12 text-muted-foreground" strokeWidth={1.5} />
          </div>
        )}
        <h3 className="text-h3 mb-astro-sm text-foreground">{title}</h3>
        {description && (
          <p className="text-body text-muted-foreground mb-astro-lg max-w-md">{description}</p>
        )}
        {action && (
          <Button onClick={action.onClick} size="lg">
            {action.label}
          </Button>
        )}
      </div>
    );
  }
);
EmptyState.displayName = 'EmptyState';

export { EmptyState, type EmptyStateProps };
