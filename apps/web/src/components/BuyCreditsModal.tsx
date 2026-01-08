/**
 * Modal for purchasing credit packs
 */

import { useState, useEffect, useCallback } from 'react';
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
import { Coins, CheckCircle2, Loader2, Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';
import {
  getStripeConfig,
  formatPriceBRL,
  redirectToCreditPurchase,
  type CreditPack,
  type CreditPackType,
} from '@/services/stripe';

interface BuyCreditsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

interface PackOption {
  key: CreditPackType;
  pack: CreditPack;
  perCredit: number;
  isBestValue: boolean;
  savingsPercent: number; // Percentage savings compared to smallest pack
}

export function BuyCreditsModal({ isOpen, onClose }: BuyCreditsModalProps) {
  const { t } = useTranslation();
  const [packs, setPacks] = useState<PackOption[]>([]);
  const [selectedPack, setSelectedPack] = useState<CreditPackType | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isPurchasing, setIsPurchasing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadCreditPacks = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const config = await getStripeConfig();
      if (!config.credit_packs) {
        setError(t('creditPurchase.notAvailable', 'Credit packs are not available at this time.'));
        return;
      }

      const packOptions: PackOption[] = [];
      let lowestPerCredit = Infinity;
      let highestPerCredit = 0;

      // Calculate per-credit cost for each pack
      for (const [key, pack] of Object.entries(config.credit_packs)) {
        const perCredit = pack.price_brl / pack.credits;
        if (perCredit < lowestPerCredit) {
          lowestPerCredit = perCredit;
        }
        if (perCredit > highestPerCredit) {
          highestPerCredit = perCredit;
        }
        packOptions.push({
          key: key as CreditPackType,
          pack,
          perCredit,
          isBestValue: false,
          savingsPercent: 0,
        });
      }

      // Mark the best value pack and calculate savings
      packOptions.forEach((p) => {
        p.isBestValue = p.perCredit === lowestPerCredit;
        // Calculate savings compared to smallest pack (highest per-credit cost)
        if (highestPerCredit > 0 && p.perCredit < highestPerCredit) {
          p.savingsPercent = Math.round(
            ((highestPerCredit - p.perCredit) / highestPerCredit) * 100
          );
        }
      });

      // Sort by credits (small, medium, large)
      packOptions.sort((a, b) => a.pack.credits - b.pack.credits);

      setPacks(packOptions);
      // Pre-select the best value pack
      const bestValue = packOptions.find((p) => p.isBestValue);
      if (bestValue) {
        setSelectedPack(bestValue.key);
      }
    } catch (err) {
      console.error('Failed to load credit packs:', err);
      setError(t('creditPurchase.loadError', 'Failed to load credit packs. Please try again.'));
    } finally {
      setIsLoading(false);
    }
  }, [t]);

  useEffect(() => {
    if (isOpen) {
      loadCreditPacks();
    }
  }, [isOpen, loadCreditPacks]);

  const handlePurchase = async () => {
    if (!selectedPack) return;

    setIsPurchasing(true);
    setError(null);
    try {
      await redirectToCreditPurchase(selectedPack);
    } catch (err) {
      console.error('Failed to start checkout:', err);
      setError(t('creditPurchase.checkoutError', 'Failed to start checkout. Please try again.'));
      setIsPurchasing(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 mb-4">
            <Coins className="h-6 w-6 text-primary" />
          </div>
          <DialogTitle className="text-center">
            {t('creditPurchase.title', 'Buy Credits')}
          </DialogTitle>
          <DialogDescription className="text-center">
            {t('creditPurchase.subtitle', 'Credits never expire!')}
          </DialogDescription>
        </DialogHeader>

        <div className="py-4">
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : error ? (
            <div className="text-center py-4">
              <p className="text-sm text-destructive">{error}</p>
              <Button variant="link" onClick={loadCreditPacks} className="mt-2">
                {t('common.tryAgain', 'Try again')}
              </Button>
            </div>
          ) : (
            <div className="space-y-3">
              {packs.map((option) => (
                <button
                  key={option.key}
                  onClick={() => setSelectedPack(option.key)}
                  className={cn(
                    'w-full p-4 rounded-xl border-2 transition-all text-left relative',
                    selectedPack === option.key
                      ? 'border-primary bg-primary/5'
                      : 'border-border hover:border-primary/50'
                  )}
                >
                  {option.isBestValue && (
                    <span className="absolute -top-2.5 right-4 px-2 py-0.5 text-xs font-medium bg-primary text-primary-foreground rounded-full">
                      {t('creditPurchase.bestValue', 'Best Value')}
                    </span>
                  )}

                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div
                        className={cn(
                          'h-5 w-5 rounded-full border-2 flex items-center justify-center',
                          selectedPack === option.key ? 'border-primary' : 'border-muted-foreground'
                        )}
                      >
                        {selectedPack === option.key && (
                          <div className="h-2.5 w-2.5 rounded-full bg-primary" />
                        )}
                      </div>
                      <div>
                        <div className="font-medium">{option.pack.name}</div>
                        <div className="text-sm text-muted-foreground">
                          {option.pack.credits} {t('credits.credits', 'credits')}
                          {option.savingsPercent > 0 && (
                            <span className="ml-2 text-green-600 dark:text-green-400 font-medium">
                              {t('creditPurchase.save', 'Save')} {option.savingsPercent}%
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-semibold">{formatPriceBRL(option.pack.price_brl)}</div>
                      <div className="text-xs text-muted-foreground">
                        {formatPriceBRL(Math.round(option.perCredit))}{' '}
                        {t('creditPurchase.perCredit', 'per credit')}
                      </div>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          )}

          <div className="mt-4 flex items-center justify-center gap-2 text-sm text-muted-foreground">
            <CheckCircle2 className="h-4 w-4 text-green-500" />
            <span>{t('creditPurchase.neverExpire', 'Purchased credits never expire')}</span>
          </div>
        </div>

        <DialogFooter className="flex-col sm:flex-row gap-2">
          <Button variant="outline" onClick={onClose} className="w-full sm:w-auto">
            {t('common.cancel', 'Cancel')}
          </Button>
          <Button
            onClick={handlePurchase}
            disabled={!selectedPack || isPurchasing || isLoading}
            className="w-full sm:w-auto"
          >
            {isPurchasing ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                {t('common.processing', 'Processing...')}
              </>
            ) : (
              <>
                <Sparkles className="h-4 w-4 mr-2" />
                {t('creditPurchase.buyNow', 'Buy Now')}
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

export default BuyCreditsModal;
