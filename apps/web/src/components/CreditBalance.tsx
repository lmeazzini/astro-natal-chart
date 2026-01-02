/**
 * Credit balance display component
 *
 * Shows the user's current credit balance with a progress indicator
 */

import { useCredits } from '@/contexts/CreditsContext';
import { getPlanDisplayName } from '@/services/credits';
import { cn } from '@/lib/utils';

interface CreditBalanceProps {
  className?: string;
  showPlan?: boolean;
  compact?: boolean;
}

export function CreditBalance({
  className,
  showPlan = false,
  compact = false,
}: CreditBalanceProps) {
  const { credits, isLoading, error } = useCredits();

  if (isLoading) {
    return (
      <div className={cn('animate-pulse', className)}>
        <div className="h-4 w-20 bg-muted rounded" />
      </div>
    );
  }

  if (error || !credits) {
    return null;
  }

  // Unlimited plan
  if (credits.is_unlimited) {
    if (compact) {
      return <span className={cn('text-sm font-medium text-primary', className)}>Unlimited</span>;
    }

    return (
      <div className={cn('flex items-center gap-2', className)}>
        <div className="flex items-center gap-1">
          <span className="text-sm font-medium">Credits:</span>
          <span className="text-sm font-bold text-primary">Unlimited</span>
        </div>
        {showPlan && (
          <span className="text-xs text-muted-foreground px-2 py-0.5 bg-primary/10 rounded-full">
            {getPlanDisplayName(credits.plan_type)}
          </span>
        )}
      </div>
    );
  }

  // Limited credits
  const percentage = credits.usage_percentage;
  const progressColor =
    percentage >= 90 ? 'bg-destructive' : percentage >= 70 ? 'bg-yellow-500' : 'bg-primary';

  if (compact) {
    return (
      <span
        className={cn(
          'text-sm font-medium',
          percentage >= 90 ? 'text-destructive' : 'text-foreground',
          className
        )}
      >
        {credits.credits_balance}/{credits.credits_limit}
      </span>
    );
  }

  return (
    <div className={cn('space-y-1', className)}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium">Credits:</span>
          <span
            className={cn(
              'text-sm font-bold',
              percentage >= 90 ? 'text-destructive' : 'text-foreground'
            )}
          >
            {credits.credits_balance}/{credits.credits_limit}
          </span>
        </div>
        {showPlan && (
          <span className="text-xs text-muted-foreground px-2 py-0.5 bg-muted rounded-full">
            {getPlanDisplayName(credits.plan_type)}
          </span>
        )}
      </div>

      {/* Progress bar */}
      <div className="h-1.5 w-full bg-muted rounded-full overflow-hidden">
        <div
          className={cn('h-full transition-all duration-300', progressColor)}
          style={{ width: `${100 - percentage}%` }}
        />
      </div>

      {/* Days until reset */}
      {credits.days_until_reset !== null && credits.days_until_reset > 0 && (
        <p className="text-xs text-muted-foreground">
          Resets in {credits.days_until_reset} day
          {credits.days_until_reset !== 1 ? 's' : ''}
        </p>
      )}
    </div>
  );
}

export default CreditBalance;
