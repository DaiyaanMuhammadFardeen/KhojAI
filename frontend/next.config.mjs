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
    'localhost'
  ],
}

export default nextConfig