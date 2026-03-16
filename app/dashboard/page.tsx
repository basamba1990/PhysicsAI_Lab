'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { createClient } from '@/lib/supabase';
import { LineChart, Line, BarChart, Bar, CartesianGrid, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { LogOut, Plus, Play, Download } from 'lucide-react';

export default function Dashboard() {
  const router = useRouter();
  const supabase = createClient();
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [simulations, setSimulations] = useState<any[]>([]);
  const [models, setModels] = useState<any[]>([]);

  useEffect(() => {
    const checkAuth = async () => {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) {
        router.push('/auth');
        return;
      }
      setUser(user);

      // Fetch simulations
      const { data: sims } = await supabase
        .from('simulations')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(10);
      setSimulations(sims || []);

      // Fetch models
      const { data: mdls } = await supabase
        .from('model_versions')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(5);
      setModels(mdls || []);

      setLoading(false);
    };
    checkAuth();
  }, [router, supabase]);

  const handleLogout = async () => {
    await supabase.auth.signOut();
    router.push('/');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-cyan-400"></div>
      </div>
    );
  }

  const comparisonData = [
    { x: 0, pinn: 0.5, cfd: 0.48, error: 0.02 },
    { x: 0.2, pinn: 0.62, cfd: 0.60, error: 0.02 },
    { x: 0.4, pinn: 0.71, cfd: 0.70, error: 0.01 },
    { x: 0.6, pinn: 0.75, cfd: 0.76, error: 0.01 },
    { x: 0.8, pinn: 0.72, cfd: 0.73, error: 0.01 },
    { x: 1.0, pinn: 0.60, cfd: 0.62, error: 0.02 },
  ];

  const trainingData = [
    { epoch: 1, trainLoss: 0.5, valLoss: 0.52, physicsLoss: 0.48 },
    { epoch: 2, trainLoss: 0.35, valLoss: 0.38, physicsLoss: 0.32 },
    { epoch: 3, trainLoss: 0.22, valLoss: 0.25, physicsLoss: 0.20 },
    { epoch: 4, trainLoss: 0.15, valLoss: 0.18, physicsLoss: 0.14 },
    { epoch: 5, trainLoss: 0.10, valLoss: 0.12, physicsLoss: 0.09 },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      {/* Header */}
      <div className="bg-slate-800 border-b border-slate-700 p-4">
        <div className="container mx-auto flex justify-between items-center">
          <h1 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-400">
            Physics AI Lab
          </h1>
          <div className="flex items-center gap-4">
            <span className="text-slate-300">{user?.email}</span>
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors"
            >
              <LogOut className="w-4 h-4" />
              Logout
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
            <h3 className="text-slate-400 text-sm mb-2">Total Simulations</h3>
            <p className="text-3xl font-bold text-cyan-400">{simulations.length}</p>
          </div>
          <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
            <h3 className="text-slate-400 text-sm mb-2">Active Models</h3>
            <p className="text-3xl font-bold text-orange-400">{models.length}</p>
          </div>
          <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
            <h3 className="text-slate-400 text-sm mb-2">Avg Accuracy</h3>
            <p className="text-3xl font-bold text-green-400">92.3%</p>
          </div>
          <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
            <h3 className="text-slate-400 text-sm mb-2">Completed</h3>
            <p className="text-3xl font-bold text-blue-400">
              {simulations.filter((s) => s.status === 'completed').length}
            </p>
          </div>
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* PINN vs CFD Comparison */}
          <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
            <h2 className="text-xl font-semibold text-cyan-400 mb-4">PINN vs CFD Comparison</h2>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={comparisonData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="x" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1e293b',
                    border: '1px solid #475569',
                  }}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="pinn"
                  stroke="#06b6d4"
                  name="PINN Prediction"
                  strokeWidth={2}
                />
                <Line
                  type="monotone"
                  dataKey="cfd"
                  stroke="#10b981"
                  name="CFD Reference"
                  strokeWidth={2}
                />
                <Line
                  type="monotone"
                  dataKey="error"
                  stroke="#f97316"
                  name="Absolute Error"
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Training History */}
          <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
            <h2 className="text-xl font-semibold text-cyan-400 mb-4">Training History</h2>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={trainingData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="epoch" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1e293b',
                    border: '1px solid #475569',
                  }}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="trainLoss"
                  stroke="#06b6d4"
                  name="Training Loss"
                  strokeWidth={2}
                />
                <Line
                  type="monotone"
                  dataKey="valLoss"
                  stroke="#10b981"
                  name="Validation Loss"
                  strokeWidth={2}
                />
                <Line
                  type="monotone"
                  dataKey="physicsLoss"
                  stroke="#f97316"
                  name="Physics Loss"
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Recent Simulations */}
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-semibold text-cyan-400">Recent Simulations</h2>
            <button className="flex items-center gap-2 px-4 py-2 bg-cyan-600 hover:bg-cyan-700 rounded-lg transition-colors">
              <Plus className="w-4 h-4" />
              New Simulation
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {simulations.slice(0, 4).map((sim) => (
              <div key={sim.id} className="bg-slate-700 border border-slate-600 rounded-lg p-4">
                <h3 className="text-cyan-400 font-semibold mb-2">{sim.title}</h3>
                <p className="text-sm text-slate-300 mb-3">{sim.description}</p>
                <div className="flex justify-between items-center">
                  <span
                    className={`px-2 py-1 rounded text-xs font-semibold ${
                      sim.status === 'completed'
                        ? 'bg-green-900 text-green-200'
                        : 'bg-blue-900 text-blue-200'
                    }`}
                  >
                    {sim.status}
                  </span>
                  <div className="flex gap-2">
                    <button className="p-2 hover:bg-slate-600 rounded transition-colors">
                      <Play className="w-4 h-4" />
                    </button>
                    <button className="p-2 hover:bg-slate-600 rounded transition-colors">
                      <Download className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
