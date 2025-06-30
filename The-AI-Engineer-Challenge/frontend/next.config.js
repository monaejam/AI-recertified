/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: process.env.NODE_ENV === 'production' 
          ? 'https://ai-engineer-challenge-5o6p6rweq-mona-jams-projects.vercel.app/api/:path*'
          : 'http://localhost:8000/api/:path*',
      },
    ];
  },
}

module.exports = nextConfig 