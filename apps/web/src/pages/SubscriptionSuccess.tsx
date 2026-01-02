/**
 * Subscription Success Page - Shown after successful Stripe checkout
 */

import { useEffect, useRef } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useAuth } from '@/contexts/AuthContext';
import { useCredits } from '@/contexts/CreditsContext';
import { amplitudeService } from '@/services/amplitude';
import { CheckCircle, Sparkles, ArrowRight } from 'lucide-react';

export function SubscriptionSuccessPage() {
  const { user } = useAuth();
  const { refreshCredits } = useCredits();
  const [searchParams] = useSearchParams();
  const hasTracked = useRef(false);

  const sessionId = searchParams.get('session_id');

  useEffect(() => {
    // Refresh credits to get the new plan
    refreshCredits();

    // Track conversion (only once)
    if (!hasTracked.current && sessionId) {
      amplitudeService.track('subscription_completed', {
        session_id: sessionId,
        source: 'stripe_checkout',
        ...(user?.id && { user_id: user.id }),
      });
      hasTracked.current = true;
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-muted/10 to-secondary/5 flex items-center justify-center p-4">
      <Card className="max-w-md w-full text-center">
        <CardHeader className="pb-4">
          <div className="mx-auto w-16 h-16 bg-green-100 dark:bg-green-900/20 rounded-full flex items-center justify-center mb-4">
            <CheckCircle className="h-8 w-8 text-green-600 dark:text-green-400" />
          </div>
          <CardTitle className="text-2xl">Assinatura confirmada!</CardTitle>
          <CardDescription>Parabéns! Sua assinatura foi ativada com sucesso.</CardDescription>
        </CardHeader>

        <CardContent className="space-y-6">
          <div className="p-4 bg-muted/50 rounded-lg space-y-2">
            <div className="flex items-center justify-center gap-2 text-primary">
              <Sparkles className="h-5 w-5" />
              <span className="font-medium">Seus créditos foram ativados</span>
            </div>
            <p className="text-sm text-muted-foreground">
              Agora você tem acesso a todas as funcionalidades premium do seu plano. Seus créditos
              serão renovados automaticamente a cada mês.
            </p>
          </div>

          <div className="space-y-3">
            <Button asChild className="w-full">
              <Link to="/dashboard">
                Ir para o Dashboard
                <ArrowRight className="h-4 w-4 ml-2" />
              </Link>
            </Button>
            <Button asChild variant="outline" className="w-full">
              <Link to="/charts">Explorar meus mapas</Link>
            </Button>
          </div>

          <p className="text-xs text-muted-foreground">
            Você receberá um email de confirmação com os detalhes da sua assinatura. Caso tenha
            dúvidas, entre em contato com nosso suporte.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
