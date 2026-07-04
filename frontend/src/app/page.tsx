"use client";

import { Download, Heart, Terminal, Zap, GitBranch, Shield } from "lucide-react";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8 bg-gradient-to-br from-slate-50 to-slate-100">
      <div className="w-full max-w-4xl mx-auto text-center space-y-12">
        {/* Header */}
        <div className="space-y-6">
          <h1 className="text-7xl font-bold tracking-tight">
            <span className="bg-gradient-to-r from-cyan-500 to-blue-600 bg-clip-text text-transparent">
              NAP
            </span>
          </h1>
          <p className="text-2xl text-slate-600 font-light">
            Nexus AI Platform
          </p>
          <p className="text-base text-slate-500 max-w-2xl mx-auto leading-relaxed">
            Engenharia de Software baseada em Inteligência Artificial —
            orquestrando agentes especializados para automatizar todo o ciclo de vida do software.
          </p>
        </div>

        {/* Features */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <FeatureCard
            icon={<Terminal className="w-6 h-6" />}
            title="CLI Interativo"
            description="Interface terminal hacker com streaming de logs em tempo real e aprovação de comandos perigosos"
          />
          <FeatureCard
            icon={<Zap className="w-6 h-6" />}
            title="Agentes IA"
            description="Múltiplos agentes especializados trabalhando em paralelo para acelerar seu desenvolvimento"
          />
          <FeatureCard
            icon={<Shield className="w-6 h-6" />}
            title="Segurança"
            description="Sistema de aprovação inteligente para comandos destrutivos e alterações críticas"
          />
        </div>

        {/* Download Section */}
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-8 shadow-lg border border-slate-200">
          <h2 className="text-2xl font-semibold text-slate-800 mb-6">
            Baixe o NAP
          </h2>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <DownloadButton
              platform="Linux (.deb)"
              filename="nap_0.2.0-1_amd64.deb"
              icon={<Download className="w-5 h-5" />}
            />
            <DownloadButton
              platform="Windows (.exe)"
              filename="nap_0.2.0-1_amd64.exe"
              icon={<Download className="w-5 h-5" />}
              disabled
            />
          </div>
          <p className="text-sm text-slate-400 mt-4">
            Versão 0.2.0 • Requer Docker e Docker Compose
          </p>
        </div>

        {/* Donate Button */}
        <div className="pt-4">
          <button
            disabled
            className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-pink-500 to-rose-500 text-white rounded-lg font-medium shadow-md opacity-50 cursor-not-allowed"
          >
            <Heart className="w-5 h-5" />
            <span>Apoie o Projeto</span>
          </button>
          <p className="text-xs text-slate-400 mt-2">
            (Funcionalidade de doação em breve)
          </p>
        </div>

        {/* Footer */}
        <div className="pt-8 border-t border-slate-200">
          <p className="text-sm text-slate-400">
            Código aberto • Construído com ♥ pela comunidade
          </p>
        </div>
      </div>
    </main>
  );
}

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <div className="bg-white/80 backdrop-blur-sm rounded-xl p-6 shadow-sm border border-slate-200 text-left">
      <div className="flex items-center gap-3 mb-3">
        <div className="p-2 bg-cyan-100 rounded-lg text-cyan-600">
          {icon}
        </div>
        <h3 className="font-semibold text-slate-800">{title}</h3>
      </div>
      <p className="text-sm text-slate-500 leading-relaxed">
        {description}
      </p>
    </div>
  );
}

function DownloadButton({
  platform,
  filename,
  icon,
  disabled = false,
}: {
  platform: string;
  filename: string;
  icon: React.ReactNode;
  disabled?: boolean;
}) {
  if (disabled) {
    return (
      <button
        disabled
        className="inline-flex items-center gap-2 px-6 py-3 bg-slate-200 text-slate-400 rounded-lg font-medium cursor-not-allowed"
      >
        {icon}
        <span>{platform}</span>
      </button>
    );
  }

  return (
    <a
      href={`/downloads/${filename}`}
      download
      className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-lg font-medium shadow-md hover:shadow-lg hover:from-cyan-600 hover:to-blue-700 transition-all"
    >
      {icon}
      <span>{platform}</span>
    </a>
  );
}