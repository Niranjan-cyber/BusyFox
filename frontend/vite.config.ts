import react from '@vitejs/plugin-react'
import { defineConfig, loadEnv } from 'vite'

/**
 * The dev proxy exists for one reason: the deployed API Gateway stage sends no CORS headers
 * (`OPTIONS /businesses/{id}` answers 404, and a GET carries no `Access-Control-Allow-Origin`),
 * so a browser on localhost cannot call it directly. Proxying through the dev server makes the
 * request same-origin and lets screens 1 and 3 be exercised against real data locally.
 *
 * It is a local development affordance, not the fix. The Amplify-hosted build talks to the API
 * from a real browser origin and needs `CorsConfiguration` on the `AWS::Serverless::HttpApi` in
 * `infra/api-gateway.yaml` plus a redeploy — see `frontend/README.md`, "Known blockers".
 *
 * Set `VITE_API_BASE_URL=/api` in `.env.local` to use it; leave it unset for fixtures.
 */
export default defineConfig(({ mode }) => {
  const apiOrigin = loadEnv(mode, process.cwd()).VITE_DEV_API_ORIGIN

  return {
    plugins: [react()],
    server: apiOrigin
      ? {
          proxy: {
            '/api': {
              target: apiOrigin,
              changeOrigin: true,
              rewrite: (path) => path.replace(/^\/api/, ''),
            },
          },
        }
      : undefined,
  }
})
