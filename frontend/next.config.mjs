/** @type {import('next').NextConfig} */

const backendPort = process.env.BACKEND_PORT || "8000";

const nextConfig = {
  reactStrictMode: true,
  output: "standalone",
  // Transpile workspace packages
  transpilePackages: [
    "@alphaforge/solar-orb-ui",
    "@alphaforge/solar-orb-ball",
    "@alphaforge/logger",
  ],
  // Proxy API calls to backend in development
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `http://localhost:${backendPort}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
