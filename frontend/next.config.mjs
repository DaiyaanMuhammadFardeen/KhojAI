/** @type {import('next').NextConfig} */
const nextConfig = {
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
  allowedDevOrigins: [
    'nationally-award-ver-syndication.trycloudflare.com',
    'holding-exam-brokers-cms.trycloudflare.com',
    'localhost'
  ],
  // Proxy API requests to Spring Boot backend
  async rewrites() {
    return [
      {
        source: '/api/v1/:path*',
        destination: 'http://localhost:8080/api/v1/:path*'
      }
    ];
  }
}

export default nextConfig