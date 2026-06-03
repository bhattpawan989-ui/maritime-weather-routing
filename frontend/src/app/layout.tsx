import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Maritime Voyage Planner',
  description: 'Plan voyages with route, weather risk, and speed guidance.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
