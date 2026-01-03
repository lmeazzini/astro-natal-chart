/**
 * Modal displayed when user has insufficient credits for an operation
 */

import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Coins, Sparkles } from 'lucide-react';

interface InsufficientCreditsModalProps {
  isOpen: boolean;
  onClose: () => void;
  featureType: string;
  requiredCredits: number;
  availableCredits: number;
}

const featureNames: Record<string, string> = {
  interpretation_basic: 'Basic Interpretation',
  interpretation_full: 'Full Interpretation',
  pdf_report: 'PDF Report',
  synastry: 'Synastry Analysis',
  solar_return: 'Solar Return',
  saturn_return: 'Saturn Return',
  longevity: 'Longevity Analysis',
  growth: 'Growth Suggestions',
  profections: 'Profections',
  transits: 'Transits',
};

export function InsufficientCreditsModal({
  isOpen,
  onClose,
  featureType,
  requiredCredits,
  availableCredits,
}: InsufficientCreditsModalProps) {
  const navigate = useNavigate();
  const { t } = useTranslation();

  const featureName = featureNames[featureType] || featureType;
  const creditsNeeded = requiredCredits - availableCredits;

  const handleUpgrade = () => {
    onClose();
    navigate('/pricing');
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-yellow-100 dark:bg-yellow-900/20 mb-4">
            <Coins className="h-6 w-6 text-yellow-600 dark:text-yellow-400" />
          </div>
          <DialogTitle className="text-center">
            {t('credits.insufficient.title', 'Insufficient Credits')}
          </DialogTitle>
          <DialogDescription className="text-center">
            {t('credits.insufficient.description', 'You need more credits to use this feature.')}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <div className="rounded-lg bg-muted/50 p-4 space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Feature:</span>
              <span className="font-medium">{featureName}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Required:</span>
              <span className="font-medium">{requiredCredits} credits</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Available:</span>
              <span className="font-medium text-destructive">{availableCredits} credits</span>
            </div>
            <div className="border-t pt-2 mt-2">
              <div className="flex justify-between text-sm font-medium">
                <span>Credits needed:</span>
                <span className="text-primary">{creditsNeeded} more</span>
              </div>
            </div>
          </div>

          <p className="text-sm text-center text-muted-foreground">
            {t(
              'credits.insufficient.upgrade_hint',
              'Upgrade your plan to get more credits and unlock premium features.'
            )}
          </p>
        </div>

        <DialogFooter className="flex-col sm:flex-row gap-2">
          <Button variant="outline" onClick={onClose} className="w-full sm:w-auto">
            {t('common.cancel', 'Cancel')}
          </Button>
          <Button onClick={handleUpgrade} className="w-full sm:w-auto">
            <Sparkles className="h-4 w-4 mr-2" />
            {t('credits.upgrade', 'Upgrade Plan')}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

export default InsufficientCreditsModal;
