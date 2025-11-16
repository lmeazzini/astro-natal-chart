# Real Astrology - Frontend

Interface web moderna para sistema de astrologia natal tradicional.

## Stack Tecnológica

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool (fast HMR)
- **TailwindCSS** - Utility-first CSS
- **React Router** - Client-side routing
- **React Query** - Server state management
- **React Hook Form** - Form handling
- **Zod** - Schema validation
- **Axios** - HTTP client

## Estrutura de Diretórios

```
src/
├── components/        # React components
│   ├── ui/            # Base UI components
│   ├── layout/        # Layout components
│   ├── auth/          # Authentication components
│   ├── chart/         # Birth chart components
│   └── geo/           # Geolocation components
├── pages/             # Page components
├── hooks/             # Custom React hooks
├── services/          # API services
├── types/             # TypeScript types
├── utils/             # Utility functions
└── styles/            # Global styles
```

## Setup Local

### Pré-requisitos

- Node.js >= 18.0.0
- npm >= 9.0.0

### Instalação

```bash
# Instalar dependências
npm install

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas configurações

# Iniciar servidor de desenvolvimento
npm run dev
```

Acesse: http://localhost:5173

## Scripts Disponíveis

```bash
# Desenvolvimento
npm run dev              # Inicia dev server com HMR

# Build
npm run build            # Build de produção
npm run preview          # Preview do build

# Qualidade de código
npm run lint             # Lint com ESLint
npm run type-check       # Type checking com TypeScript

# Testes
npm run test             # Executar testes (Vitest)
npm run test:ui          # UI de testes
npm run test:coverage    # Testes com coverage
```

## Desenvolvimento

### Componentes

Criar novos componentes em `src/components/`:

```tsx
// src/components/ui/Button.tsx
interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary';
}

export function Button({ children, onClick, variant = 'primary' }: ButtonProps) {
  return (
    <button
      onClick={onClick}
      className={cn(
        'px-4 py-2 rounded-lg font-medium transition',
        variant === 'primary' && 'bg-blue-600 text-white hover:bg-blue-700',
        variant === 'secondary' && 'bg-gray-200 text-gray-900 hover:bg-gray-300'
      )}
    >
      {children}
    </button>
  );
}
```

### Hooks Customizados

Criar hooks em `src/hooks/`:

```tsx
// src/hooks/useAuth.ts
import { useQuery } from '@tanstack/react-query';
import { getCurrentUser } from '@/services/authService';

export function useAuth() {
  const { data: user, isLoading, error } = useQuery({
    queryKey: ['currentUser'],
    queryFn: getCurrentUser,
  });

  return {
    user,
    isAuthenticated: !!user,
    isLoading,
    error,
  };
}
```

### Services (API)

Criar services em `src/services/`:

```tsx
// src/services/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor (add auth token)
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('accessToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor (handle errors)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Redirect to login
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
```

### Validação de Formulários

Usar Zod + React Hook Form:

```tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const loginSchema = z.object({
  email: z.string().email('Email inválido'),
  password: z.string().min(8, 'Senha deve ter no mínimo 8 caracteres'),
});

type LoginFormData = z.infer<typeof loginSchema>;

function LoginForm() {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = (data: LoginFormData) => {
    console.log(data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('email')} />
      {errors.email && <span>{errors.email.message}</span>}

      <input type="password" {...register('password')} />
      {errors.password && <span>{errors.password.message}</span>}

      <button type="submit">Entrar</button>
    </form>
  );
}
```

## Variáveis de Ambiente

```env
# API URL
VITE_API_URL=http://localhost:8000

# OAuth2 Client IDs
VITE_GOOGLE_CLIENT_ID=your-google-client-id
VITE_GITHUB_CLIENT_ID=your-github-client-id
```

Acessar no código:

```tsx
const apiUrl = import.meta.env.VITE_API_URL;
```

## Build para Produção

```bash
# Build
npm run build

# Output: dist/

# Preview local do build
npm run preview
```

### Deploy

#### Vercel
```bash
npm install -g vercel
vercel
```

#### Netlify
```bash
npm install -g netlify-cli
netlify deploy --prod
```

#### Docker
```bash
# Build imagem
docker build -t astro-web --target production .

# Run container
docker run -d -p 80:80 astro-web
```

## Testes

```bash
# Executar testes
npm run test

# Watch mode
npm run test -- --watch

# Coverage
npm run test:coverage
```

Exemplo de teste:

```tsx
// src/components/Button.test.tsx
import { render, screen } from '@testing-library/react';
import { Button } from './Button';

test('renders button with text', () => {
  render(<Button>Click me</Button>);
  expect(screen.getByText('Click me')).toBeInTheDocument();
});
```

## Estilo e Boas Práticas

### Componentes
- Use TypeScript com tipos explícitos
- Prefira componentes funcionais com hooks
- Extraia lógica complexa para custom hooks
- Mantenha componentes pequenos e focados

### Estilos
- Use Tailwind CSS para estilização
- Agrupe classes relacionadas
- Use o utilitário `cn()` para classes condicionais

### Performance
- Use React.memo para componentes caros
- Lazy load rotas e componentes pesados
- Otimize imagens (WebP, lazy loading)
- Use React Query para cache de dados

### Acessibilidade
- Use HTML semântico
- Adicione ARIA labels quando necessário
- Teste navegação por teclado
- Garanta contraste adequado

## Troubleshooting

### Port 5173 em uso
```bash
# Mudar porta no vite.config.ts
server: { port: 3000 }
```

### Erros de TypeScript
```bash
# Limpar cache e reinstalar
rm -rf node_modules dist
npm install
```

### Build lento
```bash
# Usar SWC (experimental)
# Instalar plugin vite-plugin-react-swc
```

## Contribuindo

1. Seguir ESLint e Prettier
2. Escrever testes para novas features
3. Usar Conventional Commits
4. Manter componentes tipados
5. Documentar componentes complexos

## Licença

[Definir licença]
