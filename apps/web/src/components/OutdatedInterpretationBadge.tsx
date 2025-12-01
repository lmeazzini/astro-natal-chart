/**
 * Badge to display when an interpretation is outdated (prompt version changed)
 */

import { useTranslation } from 'react-i18next';
import { AlertTriangle } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { InfoTooltip } from './InfoTooltip';

interface OutdatedInterpretationBadgeProps {
  isOutdated?: boolean;
  promptVersion?: string;
  onRegenerate?: () => void;
}

export function OutdatedInterpretationBadge({
  isOutdated,
  promptVersion,
}: OutdatedInterpretationBadgeProps) {
  const { t } = useTranslation();

  if (!isOutdated) {
    return null;
  }

  return (
    <div className="flex items-center gap-2">
      <Badge
        variant="outline"
        className="flex items-center gap-1.5 border-amber-500 text-amber-700 dark:text-amber-400"
      >
        <AlertTriangle className="h-3 w-3" />
        {t('interpretations.outdated', { defaultValue: 'Outdated' })}
      </Badge>
      <InfoTooltip
        content={t('interpretations.outdatedTooltip', {
          defaultValue:
            'This interpretation was generated with an older prompt version ({{version}}). Click "Refresh AI" to regenerate with the latest version.',
          version: promptVersion || 'unknown',
        })}
        side="right"
      />
    </div>
  );
}
