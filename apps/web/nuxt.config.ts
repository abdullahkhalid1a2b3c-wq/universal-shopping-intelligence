// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: true },

  app: {
    head: {
      title: 'FitSense — Universal Fit Intelligence',
      htmlAttrs: {
        class: 'dark',
        style: 'color-scheme: dark;',
      },
      link: [
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
        {
          rel: 'stylesheet',
          href: 'https://fonts.googleapis.com/css2?family=Noto+Naskh+Arabic:wght@400;500;600;700&family=Noto+Nastaliq+Urdu:wght@400;500;600;700&display=swap',
        },
      ],
    },
  },

  modules: [
    '@nuxtjs/tailwindcss',
    '@pinia/nuxt',
    '@nuxtjs/supabase',
    '@nuxtjs/i18n',
  ],

  typescript: {
    strict: true,
  },

  supabase: {
    redirect: false,
    url: process.env.SUPABASE_URL || process.env.NUXT_PUBLIC_SUPABASE_URL || 'https://zoxobxpjgottuhrezgie.supabase.co',
    key: process.env.SUPABASE_KEY || process.env.NUXT_PUBLIC_SUPABASE_KEY || 'sb_publishable_jJPwjDyQmg7s5zZZGxMJcQ_JwzWSVC-',
  },

  i18n: {
    locales: [
      { code: 'en', name: 'English', file: 'en.json', dir: 'ltr' },
      { code: 'ur', name: 'اردو', file: 'ur.json', dir: 'rtl' },
      { code: 'ur-roman', name: 'Roman Urdu', file: 'ur-roman.json', dir: 'ltr' },
    ],
    defaultLocale: 'en',
    lazy: false,
    langDir: 'locales',
    bundle: {
      optimizeTranslationDirective: false,
    },
    strategy: 'prefix_except_default',
  },

  runtimeConfig: {
    public: {
      apiBaseUrl: process.env.NUXT_PUBLIC_API_BASE_URL || 'http://localhost:8000',
      feedbackUrl: process.env.NUXT_PUBLIC_FEEDBACK_URL || '',
    },
  },

  compatibilityDate: '2025-01-01',
})
