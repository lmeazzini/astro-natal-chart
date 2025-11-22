/**
 * Methodology Page - Educational content about Traditional Astrology and Swiss Ephemeris
 * Issue #49 - Educational content implementation
 */

import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import {
  Book,
  Satellite,
  Star,
  Calculator,
  Check,
  ArrowLeft,
  ExternalLink,
} from 'lucide-react';

export function MethodologyPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-muted/10 to-secondary/5">
      {/* Header */}
      <nav className="bg-card/80 backdrop-blur-sm border-b border-border sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <Link
            to="/"
            className="flex items-center gap-2 hover:opacity-80 transition-opacity"
            aria-label="Página Inicial"
          >
            <img src="/logo.png" alt="Real Astrology" className="h-8 w-8" />
            <h1 className="text-2xl font-bold text-foreground">Nossa Metodologia</h1>
          </Link>
          <div className="flex items-center gap-3">
            <Button asChild variant="ghost" size="sm">
              <Link to="/">
                <ArrowLeft className="mr-2 h-4 w-4" />
                Voltar
              </Link>
            </Button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="py-16 lg:py-24">
        <div className="max-w-4xl mx-auto px-4">
          <div className="text-center mb-12 animate-fade-in">
            <h2 className="text-4xl md:text-5xl font-bold text-foreground mb-6 font-display">
              Astrologia Tradicional com Precisão Astronômica
            </h2>
            <p className="text-lg text-muted-foreground max-w-3xl mx-auto leading-relaxed">
              Descubra como combinamos técnicas milenares da astrologia clássica com a tecnologia mais
              avançada de cálculos astronômicos para oferecer mapas natais precisos e confiáveis.
            </p>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <section className="pb-16 lg:pb-24">
        <div className="max-w-4xl mx-auto px-4 space-y-12">
          {/* Traditional Astrology */}
          <Card className="border-0 shadow-xl">
            <CardHeader>
              <div className="flex items-center gap-4 mb-4">
                <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
                  <Book className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <CardTitle className="text-3xl font-display">Astrologia Tradicional</CardTitle>
                  <CardDescription className="text-base mt-1">
                    Técnicas clássicas validadas por séculos de prática
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <h4 className="text-xl font-semibold mb-3 flex items-center gap-2">
                  <Star className="h-5 w-5 text-primary" />
                  O que é Astrologia Tradicional?
                </h4>
                <p className="text-muted-foreground leading-relaxed mb-4">
                  Astrologia Tradicional é o termo usado para descrever as práticas astrológicas desenvolvidas
                  na antiguidade clássica (Grécia e Roma) e aperfeiçoadas durante a Idade Média e Renascimento.
                  Diferentemente da astrologia moderna (pós-século XX), que enfatiza aspectos psicológicos e
                  de autoconhecimento, a astrologia tradicional é objetiva, preditiva e baseada em dignidades planetárias.
                </p>
                <p className="text-muted-foreground leading-relaxed">
                  Nossa plataforma implementa técnicas da <strong>Astrologia Helenística</strong> (período greco-romano,
                  100 a.C. - 600 d.C.) e <strong>Astrologia Medieval</strong> (período medieval europeu e árabe,
                  700 d.C. - 1700 d.C.), seguindo textos de autores clássicos como Ptolemeu, Vettius Valens,
                  Dorotheus de Sidon, Abu Ma'shar e William Lilly.
                </p>
              </div>

              <Separator />

              <div>
                <h4 className="text-xl font-semibold mb-3">Técnicas Implementadas</h4>
                <div className="space-y-4">
                  <div>
                    <h5 className="font-semibold text-foreground mb-2 flex items-center gap-2">
                      <Check className="h-4 w-4 text-primary" />
                      1. Dignidades Essenciais
                    </h5>
                    <p className="text-muted-foreground text-sm leading-relaxed ml-6">
                      Sistema de pontuação que avalia a força e qualidade de um planeta em um signo:
                    </p>
                    <ul className="text-sm text-muted-foreground space-y-1 ml-10 mt-2">
                      <li><strong>Domicílio (+5)</strong>: Planeta em seu próprio signo (ex: Marte em Áries)</li>
                      <li><strong>Exaltação (+4)</strong>: Planeta em seu signo de exaltação (ex: Sol em Áries)</li>
                      <li><strong>Triplicidade (+3)</strong>: Planeta regente do elemento do signo</li>
                      <li><strong>Termo (+2)</strong>: Planeta tem domínio sobre graus específicos</li>
                      <li><strong>Face (+1)</strong>: Planeta governa decano (10°) do signo</li>
                      <li><strong>Peregrino (0)</strong>: Planeta sem dignidades ou debilidades</li>
                      <li><strong>Detrimento (-5)</strong>: Planeta no signo oposto ao seu domicílio</li>
                      <li><strong>Queda (-4)</strong>: Planeta no signo oposto à sua exaltação</li>
                    </ul>
                  </div>

                  <div>
                    <h5 className="font-semibold text-foreground mb-2 flex items-center gap-2">
                      <Check className="h-4 w-4 text-primary" />
                      2. Análise de Seita (Dia/Noite)
                    </h5>
                    <p className="text-muted-foreground text-sm leading-relaxed ml-6">
                      Determinamos se o mapa é <strong>diurno</strong> (Sol acima do horizonte) ou{' '}
                      <strong>noturno</strong> (Sol abaixo do horizonte). Planetas são classificados como:
                    </p>
                    <ul className="text-sm text-muted-foreground space-y-1 ml-10 mt-2">
                      <li><strong>Diurnos</strong>: Sol, Júpiter, Saturno (melhor performance em mapas diurnos)</li>
                      <li><strong>Noturnos</strong>: Lua, Vênus, Marte (melhor performance em mapas noturnos)</li>
                      <li><strong>Neutros</strong>: Mercúrio (adapta-se ao contexto)</li>
                    </ul>
                    <p className="text-muted-foreground text-sm leading-relaxed ml-6 mt-2">
                      Planetas em seita (alinhados com o tipo de mapa) expressam-se de forma mais harmônica.
                      Maléficos fora de seita (ex: Saturno em mapa noturno) podem causar mais dificuldades.
                    </p>
                  </div>

                  <div>
                    <h5 className="font-semibold text-foreground mb-2 flex items-center gap-2">
                      <Check className="h-4 w-4 text-primary" />
                      3. Análise de Temperamento
                    </h5>
                    <p className="text-muted-foreground text-sm leading-relaxed ml-6">
                      Calculamos o temperamento dominante da natividade baseado nos <strong>4 elementos</strong>{' '}
                      (Fogo, Terra, Ar, Água) e <strong>4 qualidades</strong> (Quente, Frio, Seco, Úmido).
                      O temperamento revela características físicas, emocionais e comportamentais inatas.
                    </p>
                    <ul className="text-sm text-muted-foreground space-y-1 ml-10 mt-2">
                      <li><strong>Colérico</strong> (Fogo): Quente e Seco - enérgico, impulsivo, assertivo</li>
                      <li><strong>Melancólico</strong> (Terra): Frio e Seco - pragmático, estável, introspectivo</li>
                      <li><strong>Sanguíneo</strong> (Ar): Quente e Úmido - sociável, otimista, adaptável</li>
                      <li><strong>Fleumático</strong> (Água): Frio e Úmido - emocional, empático, intuitivo</li>
                    </ul>
                  </div>

                  <div>
                    <h5 className="font-semibold text-foreground mb-2 flex items-center gap-2">
                      <Check className="h-4 w-4 text-primary" />
                      4. Senhor da Natividade (Lord of the Nativity)
                    </h5>
                    <p className="text-muted-foreground text-sm leading-relaxed ml-6">
                      Identificamos o planeta que governa a natividade através de um algoritmo de pontuação que considera:
                      dignidades essenciais, regência do Ascendente, regência da Lua, regência do Sol (em mapas diurnos),
                      regência da Parte da Fortuna, e planetas angulares. O Senhor da Natividade representa temas centrais
                      e características dominantes da vida do nativo.
                    </p>
                  </div>
                </div>
              </div>

              <Separator />

              <div className="bg-muted/50 p-4 rounded-lg">
                <h5 className="font-semibold text-foreground mb-2">
                  Astrologia Tradicional vs. Moderna
                </h5>
                <div className="space-y-2 text-sm text-muted-foreground">
                  <p><strong>Tradicional:</strong> Objetiva, preditiva, baseada em dignidades e disposições</p>
                  <p><strong>Moderna:</strong> Psicológica, interpretativa, foca em arquétipos e autoconhecimento</p>
                  <p className="pt-2 italic">
                    <strong>Nossa abordagem:</strong> Priorizamos técnicas tradicionais por serem matematicamente
                    definidas e empiricamente testadas ao longo de séculos, oferecendo maior precisão e
                    consistência nas interpretações.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Swiss Ephemeris */}
          <Card className="border-0 shadow-xl">
            <CardHeader>
              <div className="flex items-center gap-4 mb-4">
                <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
                  <Satellite className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <CardTitle className="text-3xl font-display">Swiss Ephemeris</CardTitle>
                  <CardDescription className="text-base mt-1">
                    A biblioteca de efemérides mais precisa do mundo
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <h4 className="text-xl font-semibold mb-3 flex items-center gap-2">
                  <Calculator className="h-5 w-5 text-primary" />
                  O que é Swiss Ephemeris?
                </h4>
                <p className="text-muted-foreground leading-relaxed mb-4">
                  <strong>Swiss Ephemeris</strong> é uma biblioteca de código aberto desenvolvida pela Astrodienst AG
                  (Suíça) que fornece posições planetárias de altíssima precisão. É a ferramenta padrão utilizada por
                  astrólogos profissionais, pesquisadores astronômicos e desenvolvedores de software astrológico em todo o mundo.
                </p>
                <p className="text-muted-foreground leading-relaxed">
                  A biblioteca é baseada nas efemérides <strong>JPL DE431</strong> da NASA/JPL (Jet Propulsion Laboratory),
                  as mesmas utilizadas em missões espaciais reais como Voyager, Cassini e Mars Rovers. Isso garante que
                  nossos cálculos tenham o mesmo nível de confiabilidade usado pela exploração espacial.
                </p>
              </div>

              <Separator />

              <div>
                <h4 className="text-xl font-semibold mb-3">Especificações Técnicas</h4>
                <div className="space-y-3">
                  <div className="flex items-start gap-3">
                    <Check className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="font-semibold text-foreground">Precisão Inferior a 1 Arcsecond</p>
                      <p className="text-sm text-muted-foreground">
                        Erro médio de posicionamento &lt; 0.001° (menos de 1 segundo de arco). Para comparação,
                        a Lua aparente no céu tem 1800 arcseconds de diâmetro - nossa precisão é 1800× menor que isso.
                      </p>
                    </div>
                  </div>

                  <div className="flex items-start gap-3">
                    <Check className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="font-semibold text-foreground">Cobertura Temporal de 13.000 Anos</p>
                      <p className="text-sm text-muted-foreground">
                        Cálculos válidos de 10.000 a.C. até 10.000 d.C., permitindo análise histórica de eventos
                        antigos (nascimento de Jesus Cristo, fundação de Roma) e previsões futuras de longo prazo.
                      </p>
                    </div>
                  </div>

                  <div className="flex items-start gap-3">
                    <Check className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="font-semibold text-foreground">Efemérides JPL DE431 (NASA)</p>
                      <p className="text-sm text-muted-foreground">
                        Utiliza os mesmos dados de integração numérica do sistema solar desenvolvidos pelo
                        Jet Propulsion Laboratory da NASA, incluindo ajustes para Relatividade Geral de Einstein,
                        perturbações gravitacionais de asteroides e efeitos de maré.
                      </p>
                    </div>
                  </div>

                  <div className="flex items-start gap-3">
                    <Check className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="font-semibold text-foreground">Código Aberto e Auditável</p>
                      <p className="text-sm text-muted-foreground">
                        Swiss Ephemeris é software livre sob licença GPL/AGPL, permitindo que qualquer pessoa
                        verifique os algoritmos e validação dos cálculos. Nenhum "algoritmo secreto" ou "caixa-preta".
                      </p>
                    </div>
                  </div>

                  <div className="flex items-start gap-3">
                    <Check className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="font-semibold text-foreground">Validação Científica</p>
                      <p className="text-sm text-muted-foreground">
                        Comparações com observações astronômicas reais (ocultações, eclipses, trânsitos) confirmam
                        a precisão das previsões. Erros residuais são da ordem de milissegundos de arco.
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              <Separator />

              <div>
                <h4 className="text-xl font-semibold mb-3">Por Que Precisão Importa?</h4>
                <div className="space-y-3 text-muted-foreground">
                  <p className="leading-relaxed">
                    <strong>1. Casas Astrológicas Sensíveis ao Tempo:</strong> Diferenças de apenas 4 minutos
                    na hora de nascimento podem alterar completamente a posição das cúspides das casas. Com
                    precisão de 1 arcsecond, garantimos cálculos confiáveis mesmo quando o horário de nascimento
                    é aproximado (±5-10 minutos).
                  </p>
                  <p className="leading-relaxed">
                    <strong>2. Aspectos Partis e Orbes Exatas:</strong> Para determinar se dois planetas estão
                    em aspecto partil (orbe de ±1°), precisamos de posições planetárias extremamente precisas.
                    Aspectos partis são considerados mais fortes e significativos na astrologia tradicional.
                  </p>
                  <p className="leading-relaxed">
                    <strong>3. Progressões e Direções Primárias:</strong> Técnicas preditivas avançadas (não
                    implementadas ainda) requerem precisão de arcsecond para calcular corretamente o timing de
                    eventos futuros. Nossa infraestrutura já está preparada para essas funcionalidades.
                  </p>
                  <p className="leading-relaxed">
                    <strong>4. Confiabilidade Histórica:</strong> Para mapas de figuras históricas (séculos passados),
                    pequenos erros de cálculo podem se acumular. Swiss Ephemeris mantém precisão mesmo para datas
                    antigas, permitindo estudos de astrologia histórica confiáveis.
                  </p>
                </div>
              </div>

              <Separator />

              <div className="bg-muted/50 p-4 rounded-lg">
                <h5 className="font-semibold text-foreground mb-2">
                  Comparação com Outras Plataformas
                </h5>
                <div className="space-y-2 text-sm text-muted-foreground">
                  <p>
                    <strong>Plataformas comerciais genéricas:</strong> Muitas usam algoritmos simplificados ou
                    efemérides de baixa precisão (erros de 10-30 arcseconds), suficientes para horóscopos
                    populares mas inadequados para análise profissional.
                  </p>
                  <p>
                    <strong>Software profissional (Janus, Solar Fire):</strong> Também utilizam Swiss Ephemeris,
                    oferecendo precisão equivalente à nossa. Nosso diferencial é combinar essa precisão com
                    interface moderna, código aberto e técnicas tradicionais documentadas.
                  </p>
                  <p className="pt-2 italic">
                    <strong>Nossa garantia:</strong> Mesma precisão de software profissional pago, mas com
                    transparência total, código auditável e acesso gratuito.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Implementation Details */}
          <Card className="border-0 shadow-xl">
            <CardHeader>
              <CardTitle className="text-2xl font-display">Detalhes de Implementação</CardTitle>
              <CardDescription className="text-base mt-1">
                Transparência total sobre nossas técnicas de cálculo
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h5 className="font-semibold text-foreground mb-2">Sistemas de Casas Suportados</h5>
                <ul className="text-sm text-muted-foreground space-y-1 ml-4">
                  <li><strong>Placidus</strong> (padrão): Sistema mais popular, baseado em divisão de tempo</li>
                  <li><strong>Koch</strong>: Similar a Placidus, popular na Europa</li>
                  <li><strong>Equal House</strong>: Divisão igual de 30° a partir do Ascendente</li>
                  <li><strong>Whole Sign</strong>: Sistema tradicional helenístico (signos inteiros)</li>
                  <li><strong>Campanus</strong>: Baseado em círculo primário</li>
                  <li><strong>Regiomontanus</strong>: Sistema medieval, preserva ângulos</li>
                </ul>
              </div>

              <Separator className="my-4" />

              <div>
                <h5 className="font-semibold text-foreground mb-2">Planetas Calculados</h5>
                <p className="text-sm text-muted-foreground mb-2">
                  Sol, Lua, Mercúrio, Vênus, Marte, Júpiter, Saturno, Urano, Netuno, Plutão, Nodo Norte (True Node)
                </p>
                <p className="text-xs text-muted-foreground italic">
                  Nota: Planetas modernos (Urano, Netuno, Plutão) são calculados mas não utilizados em técnicas
                  tradicionais de dignidades e seita (que consideram apenas os 7 planetas clássicos).
                </p>
              </div>

              <Separator className="my-4" />

              <div>
                <h5 className="font-semibold text-foreground mb-2">Aspectos Detectados</h5>
                <ul className="text-sm text-muted-foreground space-y-1 ml-4">
                  <li><strong>Maiores:</strong> Conjunção (0°), Oposição (180°), Trígono (120°), Quadratura (90°), Sextil (60°)</li>
                  <li><strong>Menores:</strong> Quincunx (150°), Semisextil (30°), Semiquadratura (45°), Sesquiquadrado (135°)</li>
                  <li><strong>Orbes:</strong> 8° para aspectos maiores, 3° para aspectos menores (configurável)</li>
                  <li><strong>Aplicando/Separando:</strong> Determinado pela velocidade relativa dos planetas</li>
                </ul>
              </div>

              <Separator className="my-4" />

              <div>
                <h5 className="font-semibold text-foreground mb-2">Funcionalidades Futuras</h5>
                <ul className="text-sm text-muted-foreground space-y-1 ml-4">
                  <li>Cálculo da Parte da Fortuna e outras partes árabes</li>
                  <li>Estrelas fixas e suas conjunções com planetas</li>
                  <li>Direções Primárias e Secundárias</li>
                  <li>Retornos Solares e Lunares</li>
                  <li>Sinastria (comparação de mapas) com técnicas tradicionais</li>
                </ul>
              </div>
            </CardContent>
          </Card>

          {/* References */}
          <Card className="border-0 shadow-xl">
            <CardHeader>
              <CardTitle className="text-2xl font-display">Referências e Leituras Recomendadas</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h5 className="font-semibold text-foreground mb-2">Textos Clássicos de Astrologia</h5>
                <ul className="text-sm text-muted-foreground space-y-2">
                  <li>
                    <strong>Tetrabiblos</strong> - Claudius Ptolemy (século II d.C.)<br />
                    <span className="text-xs">Fundação da astrologia helenística ocidental</span>
                  </li>
                  <li>
                    <strong>Anthology</strong> - Vettius Valens (século II d.C.)<br />
                    <span className="text-xs">Técnicas práticas e exemplos de mapas reais</span>
                  </li>
                  <li>
                    <strong>Carmen Astrologicum</strong> - Dorotheus de Sidon (século I d.C.)<br />
                    <span className="text-xs">Texto helenístico sobre delineação e predição</span>
                  </li>
                  <li>
                    <strong>The Great Introduction</strong> - Abu Ma'shar (século IX d.C.)<br />
                    <span className="text-xs">Síntese medieval persa de astrologia tradicional</span>
                  </li>
                  <li>
                    <strong>Christian Astrology</strong> - William Lilly (1647)<br />
                    <span className="text-xs">Astrologia tradicional inglesa renascentista</span>
                  </li>
                </ul>
              </div>

              <Separator />

              <div>
                <h5 className="font-semibold text-foreground mb-2">Documentação Técnica</h5>
                <ul className="text-sm text-muted-foreground space-y-2">
                  <li>
                    <a
                      href="https://www.astro.com/swisseph/swephinfo_e.htm"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1 text-primary hover:underline"
                    >
                      Swiss Ephemeris Official Documentation
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  </li>
                  <li>
                    <a
                      href="https://ssd.jpl.nasa.gov/planets/eph_export.html"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1 text-primary hover:underline"
                    >
                      JPL Planetary and Lunar Ephemerides
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  </li>
                  <li>
                    <a
                      href="https://github.com/lmeazzini/astro-natal-chart"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1 text-primary hover:underline"
                    >
                      Nosso Código-Fonte (GitHub)
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  </li>
                </ul>
              </div>

              <Separator />

              <div>
                <h5 className="font-semibold text-foreground mb-2">Autores Contemporâneos</h5>
                <ul className="text-sm text-muted-foreground space-y-2">
                  <li><strong>Chris Brennan</strong> - "Hellenistic Astrology: The Study of Fate and Fortune"</li>
                  <li><strong>Demetra George</strong> - "Ancient Astrology in Theory and Practice"</li>
                  <li><strong>Robert Hand</strong> - "Night & Day: Planetary Sect in Astrology"</li>
                  <li><strong>Benjamin Dykes</strong> - Traduções de textos medievais e persas</li>
                </ul>
              </div>
            </CardContent>
          </Card>

          {/* CTA */}
          <div className="text-center py-8">
            <h3 className="text-2xl font-bold mb-4">Pronto para Explorar Seu Mapa Natal?</h3>
            <p className="text-muted-foreground mb-6 max-w-2xl mx-auto">
              Experimente a combinação de astrologia tradicional com precisão astronômica profissional.
              Crie sua conta gratuitamente e descubra os segredos do seu céu de nascimento.
            </p>
            <div className="flex gap-4 justify-center">
              <Button asChild size="lg">
                <Link to="/register">Criar Conta Grátis</Link>
              </Button>
              <Button asChild variant="outline" size="lg">
                <Link to="/charts/new">Ver Exemplo de Mapa</Link>
              </Button>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
