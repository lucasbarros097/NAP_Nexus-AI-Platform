import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "NAP - Nexus AI Platform",
  description:
    "Plataforma de Engenharia de Software baseada em Inteligência Artificial",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR">
      <body className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
        {children}
      </body>
    </html>
  );
}