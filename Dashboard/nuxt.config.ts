import tailwindcss from "@tailwindcss/vite";

export default defineNuxtConfig({
  compatibilityDate: "2024-11-01",
  devtools: { enabled: true },

  // 1) Inject viewport meta so everything scales correctly
  app: {
    head: {
      meta: [
        { charset: "utf-8" },
        {
          name: "viewport",
          content: "width=device-width, initial-scale=1",
        },
      ],
    },
  },

  // Global CSS
  css: ['~/assets/css/main.css'],

  // Vite plugins
  vite: {
    plugins: [tailwindcss()]
  },

  // Nuxt modules
  modules: [
    "@nuxt/icon"
  ],

  // Transpile vue-chartjs for compatibility
  build: {
    transpile: ['vue-chartjs']
  }
});
