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
}

export default nextConfig