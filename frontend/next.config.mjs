/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: "standalone",
  // Transpile workspace packages
  transpilePackages: ["@alphaforge/solar-orb-ui", "@alphaforge/logger"],
  // Proxy API calls to backend in development
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://localhost:8000/api/:path*",
      },
    ];
  },
};

export default nextConfig;
