'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { createClient } from '@/lib/supabase';
import { ArrowRight, Zap, BarChart3, Shield, Cpu } from 'lucide-react';

export default function Home() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const supabase = createClient();

  useEffect(() => {
    const checkAuth = async () => {
      const { data: { user } } = await supabase.auth.getUser();
      setUser(user);
      setLoading(false);
      if (user) {
        router.push('/dashboard');
      }
    };
    checkAuth();
  }, [router, supabase]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-cyan-400"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-3xl mx-auto text-center">
          <h1 className="text-5xl font-bold mb-4 text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-400">
            Physics AI Lab
          </h1>
          <p className="text-xl text-slate-300 mb-8">
            Advanced Physics-Informed Neural Networks (PINN) and Physics-Informed Operator Networks (PINO) Simulation Platform
          </p>

          <div className="bg-slate-800 border border-slate-700 rounded-lg p-8 mb-8">
            <h2 className="text-2xl font-semibold text-cyan-400 mb-4">
              Get Started
            </h2>
            <p className="text-slate-300 mb-6">
              Sign in to access advanced physics simulations, model management, and real-time analytics.
            </p>
            <button
              onClick={() => router.push('/auth')}
              className="inline-flex items-center px-6 py-3 bg-cyan-600 hover:bg-cyan-700 text-white font-semibold rounded-lg transition-colors"
            >
              Sign In
              <ArrowRight className="ml-2 w-5 h-5" />
            </button>
          </div>

          {/* Features */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mt-12">
            <div className="bg-slate-800 border border-slate-700 hover:border-cyan-500 transition-colors rounded-lg p-6">
              <Zap className="w-8 h-8 text-cyan-400 mb-2 mx-auto" />
              <h3 className="text-cyan-400 font-semibold mb-2">Fast Inference</h3>
              <p className="text-sm text-slate-300">
                ONNX-powered PINN models for real-time predictions
              </p>
            </div>

            <div className="bg-slate-800 border border-slate-700 hover:border-orange-500 transition-colors rounded-lg p-6">
              <BarChart3 className="w-8 h-8 text-orange-400 mb-2 mx-auto" />
              <h3 className="text-orange-400 font-semibold mb-2">Analytics</h3>
              <p className="text-sm text-slate-300">
                Comprehensive visualizations and performance metrics
              </p>
            </div>

            <div className="bg-slate-800 border border-slate-700 hover:border-green-500 transition-colors rounded-lg p-6">
              <Shield className="w-8 h-8 text-green-400 mb-2 mx-auto" />
              <h3 className="text-green-400 font-semibold mb-2">Ethics</h3>
              <p className="text-sm text-slate-300">
                Built-in bias detection and fairness validation
              </p>
            </div>

            <div className="bg-slate-800 border border-slate-700 hover:border-blue-500 transition-colors rounded-lg p-6">
              <Cpu className="w-8 h-8 text-blue-400 mb-2 mx-auto" />
              <h3 className="text-blue-400 font-semibold mb-2">Scalable</h3>
              <p className="text-sm text-slate-300">
                Cloud-native architecture with Edge Functions
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
