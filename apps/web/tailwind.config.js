/** @type {import('tailwindcss').Config} */
export default {
    darkMode: ['class'],
    content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
  	extend: {
  		colors: {
  			border: 'hsl(var(--border))',
  			input: 'hsl(var(--input))',
  			ring: 'hsl(var(--ring))',
  			background: 'hsl(var(--background))',
  			foreground: 'hsl(var(--foreground))',
  			primary: {
  				DEFAULT: 'hsl(var(--primary))',
  				foreground: 'hsl(var(--primary-foreground))'
  			},
  			secondary: {
  				DEFAULT: 'hsl(var(--secondary))',
  				foreground: 'hsl(var(--secondary-foreground))'
  			},
  			destructive: {
  				DEFAULT: 'hsl(var(--destructive))',
  				foreground: 'hsl(var(--destructive-foreground))'
  			},
  			muted: {
  				DEFAULT: 'hsl(var(--muted))',
  				foreground: 'hsl(var(--muted-foreground))'
  			},
  			accent: {
  				DEFAULT: 'hsl(var(--accent))',
  				foreground: 'hsl(var(--accent-foreground))'
  			},
  			popover: {
  				DEFAULT: 'hsl(var(--popover))',
  				foreground: 'hsl(var(--popover-foreground))'
  			},
  			card: {
  				DEFAULT: 'hsl(var(--card))',
  				foreground: 'hsl(var(--card-foreground))'
  			},
  			chart: {
  				'1': 'hsl(var(--chart-1))',
  				'2': 'hsl(var(--chart-2))',
  				'3': 'hsl(var(--chart-3))',
  				'4': 'hsl(var(--chart-4))',
  				'5': 'hsl(var(--chart-5))'
  			},
  			// Astro Essence planet colors
  			planet: {
  				sun: '#F59E0B',      // Amber-500
  				moon: '#93C5FD',     // Blue-300
  				mercury: '#A78BFA',  // Purple-400
  				venus: '#F9A8D4',    // Pink-300
  				mars: '#EF4444',     // Red-500
  				jupiter: '#3B82F6',  // Blue-500
  				saturn: '#64748B',   // Slate-500
  				uranus: '#06B6D4',   // Cyan-500
  				neptune: '#8B5CF6',  // Violet-500
  				pluto: '#7C3AED'     // Violet-600
  			}
  		},
  			borderRadius: {
  				lg: 'var(--radius)',
  				md: 'calc(var(--radius) - 2px)',
  				sm: 'calc(var(--radius) - 4px)',
  				// Astro Essence specific radii
  				'astro-sm': '12px',
  				'astro-md': '16px',
  				'astro-lg': '20px',
  				'astro-xl': '24px'
  			},
  			fontFamily: {
  				sans: [
  					'Inter',
  					'system-ui',
  					'sans-serif'
  				],
  				// Astro Essence fonts
  				display: [
  					'Playfair Display',
  					'Georgia',
  					'serif'
  				],
  				body: [
  					'Inter',
  					'system-ui',
  					'sans-serif'
  				],
  				mono: [
  					'Inter Tight',
  					'ui-monospace',
  					'monospace'
  				]
  			},
  			// Astro Essence spacing system (8px base)
  			spacing: {
  				'astro-xs': '4px',
  				'astro-sm': '8px',
  				'astro-md': '16px',
  				'astro-lg': '24px',
  				'astro-xl': '32px',
  				'astro-2xl': '48px',
  				'astro-3xl': '64px',
  				'astro-4xl': '96px'
  			},
  			// Astro Essence animations
  			animation: {
  				'fade-in': 'fadeIn 0.4s ease-out',
  				'slide-in-up': 'slideInUp 0.3s ease-out',
  				'slide-in-down': 'slideInDown 0.3s ease-out',
  				'shimmer': 'shimmer 2s linear infinite',
  				'float': 'float 3s ease-in-out infinite'
  			},
  			keyframes: {
  				fadeIn: {
  					'0%': { opacity: '0' },
  					'100%': { opacity: '1' }
  				},
  				slideInUp: {
  					'0%': { transform: 'translateY(10px)', opacity: '0' },
  					'100%': { transform: 'translateY(0)', opacity: '1' }
  				},
  				slideInDown: {
  					'0%': { transform: 'translateY(-10px)', opacity: '0' },
  					'100%': { transform: 'translateY(0)', opacity: '1' }
  				},
  				shimmer: {
  					'0%': { backgroundPosition: '-200% 0' },
  					'100%': { backgroundPosition: '200% 0' }
  				},
  				float: {
  					'0%, 100%': { transform: 'translateY(0px)' },
  					'50%': { transform: 'translateY(-10px)' }
  				}
  			},
  			// Astro Essence timing functions
  			transitionTimingFunction: {
  				'ease-smooth': 'cubic-bezier(0.4, 0, 0.2, 1)',
  				'ease-bounce': 'cubic-bezier(0.68, -0.55, 0.265, 1.55)'
  			}
  		}
  	},
  plugins: [require("tailwindcss-animate")],
};
