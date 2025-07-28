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
}

export default nextConfig
