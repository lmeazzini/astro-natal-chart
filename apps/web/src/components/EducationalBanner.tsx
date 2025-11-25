import { Lightbulb, X } from 'lucide-react';
import { useState } from 'react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface EducationalBannerProps {
  title: string;
  description: string | React.ReactNode;
  dismissible?: boolean;
  storageKey?: string;
  className?: string;
}

export function EducationalBanner({
  title,
  description,
  dismissible = true,
  storageKey,
  className,
}: EducationalBannerProps) {
  const [isDismissed, setIsDismissed] = useState(() => {
    if (storageKey && typeof window !== 'undefined') {
      return localStorage.getItem(storageKey) === 'true';
    }
    return false;
  });

  const handleDismiss = () => {
    setIsDismissed(true);
    if (storageKey && typeof window !== 'undefined') {
      localStorage.setItem(storageKey, 'true');
    }
  };

  if (isDismissed) {
    return null;
  }

  return (
    <Alert
      className={cn(
        'border-blue-200 bg-blue-50 dark:border-blue-900 dark:bg-blue-950/30',
        className
      )}
    >
      <Lightbulb className="h-5 w-5 text-blue-600 dark:text-blue-400" />
      <AlertTitle className="text-blue-900 dark:text-blue-100 pr-8">{title}</AlertTitle>
      <AlertDescription className="text-blue-800 dark:text-blue-200">
        {description}
      </AlertDescription>
      {dismissible && (
        <Button
          variant="ghost"
          size="sm"
          className="absolute top-2 right-2 h-6 w-6 p-0 hover:bg-blue-100 dark:hover:bg-blue-900"
          onClick={handleDismiss}
          aria-label="Fechar dica"
        >
          <X className="h-4 w-4 text-blue-600 dark:text-blue-400" />
        </Button>
      )}
    </Alert>
  );
}
