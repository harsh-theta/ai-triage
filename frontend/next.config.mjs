/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
  // Configure for proxy deployment with /intelligent-triage/ base path
  basePath: '/intelligent-triage',
  assetPrefix: '/intelligent-triage',
  trailingSlash: false,
  // Enable static export for nginx deployment
  output: 'export',
  distDir: 'out',
  // Ensure proper handling of static assets
  experimental: {
    appDir: true,
  },
  // Handle base path for static assets
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
      };
    }
    return config;
  },
}

export default nextConfig
