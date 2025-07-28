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
}

export default nextConfig
