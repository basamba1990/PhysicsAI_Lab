import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { Loader2, Play, Download, Plus } from "lucide-react";

export default function Dashboard() {
  const [simulations, setSimulations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedSimulation, setSelectedSimulation] = useState<any>(null);

  // Mock data for demonstration
  const mockTrainingHistory = [
    { epoch: 0, train_loss: 0.5, val_loss: 0.52, physics_loss: 0.3 },
    { epoch: 10, train_loss: 0.3, val_loss: 0.32, physics_loss: 0.2 },
    { epoch: 20, train_loss: 0.15, val_loss: 0.18, physics_loss: 0.1 },
    { epoch: 30, train_loss: 0.08, val_loss: 0.1, physics_loss: 0.05 },
    { epoch: 40, train_loss: 0.05, val_loss: 0.07, physics_loss: 0.03 },
    { epoch: 50, train_loss: 0.03, val_loss: 0.05, physics_loss: 0.02 }
  ];

  const mockPredictionComparison = [
    { x: 0.0, pinn: 0.0, cfd: 0.02, error: 0.02 },
    { x: 0.2, pinn: 0.19, cfd: 0.21, error: 0.02 },
    { x: 0.4, pinn: 0.39, cfd: 0.38, error: 0.01 },
    { x: 0.6, pinn: 0.59, cfd: 0.61, error: 0.02 },
    { x: 0.8, pinn: 0.79, cfd: 0.78, error: 0.01 },
    { x: 1.0, pinn: 1.0, cfd: 0.99, error: 0.01 }
  ];

  const mockModelMetrics = [
    { metric: "Fidelity", value: 0.95 },
    { metric: "Accuracy", value: 0.92 },
    { metric: "Precision", value: 0.88 },
    { metric: "Recall", value: 0.90 }
  ];

  useEffect(() => {
    // Simulate loading simulations
    setLoading(false);
    setSimulations([
      {
        id: 1,
        name: "Heat Transfer Simulation v1",
        status: "completed",
        created_at: new Date().toISOString(),
        fidelity: 0.95
      },
      {
        id: 2,
        name: "Fluid Flow Analysis",
        status: "running",
        created_at: new Date().toISOString(),
        progress: 65
      }
    ]);
  }, []);

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Physics AI Dashboard</h1>
          <p className="text-muted-foreground">PINN/PINO Simulation Platform</p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Total Simulations</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{simulations.length}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Model Fidelity</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">95%</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Avg Uncertainty</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">±5%</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Ethics Score</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">0.92</div>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <Tabs defaultValue="simulations" className="space-y-4">
          <TabsList>
            <TabsTrigger value="simulations">Simulations</TabsTrigger>
            <TabsTrigger value="training">Training</TabsTrigger>
            <TabsTrigger value="models">Models</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
          </TabsList>

          {/* Simulations Tab */}
          <TabsContent value="simulations">
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold">Recent Simulations</h2>
                <Button>
                  <Plus className="w-4 h-4 mr-2" />
                  New Simulation
                </Button>
              </div>

              <div className="grid gap-4">
                {simulations.map((sim) => (
                  <Card key={sim.id} className="cursor-pointer hover:bg-accent" onClick={() => setSelectedSimulation(sim)}>
                    <CardHeader>
                      <div className="flex justify-between items-start">
                        <div>
                          <CardTitle>{sim.name}</CardTitle>
                          <CardDescription>{new Date(sim.created_at).toLocaleDateString()}</CardDescription>
                        </div>
                        <div className="text-right">
                          <div className={`text-sm font-semibold ${sim.status === 'completed' ? 'text-green-600' : 'text-blue-600'}`}>
                            {sim.status.toUpperCase()}
                          </div>
                          {sim.progress && <div className="text-xs text-muted-foreground">{sim.progress}%</div>}
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="flex gap-2">
                        <Button size="sm" variant="outline">
                          <Play className="w-4 h-4 mr-2" />
                          Run
                        </Button>
                        <Button size="sm" variant="outline">
                          <Download className="w-4 h-4 mr-2" />
                          Export
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          </TabsContent>

          {/* Training Tab */}
          <TabsContent value="training">
            <Card>
              <CardHeader>
                <CardTitle>Training History</CardTitle>
                <CardDescription>Model loss and physics loss over epochs</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={400}>
                  <LineChart data={mockTrainingHistory}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="epoch" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="train_loss" stroke="#8884d8" />
                    <Line type="monotone" dataKey="val_loss" stroke="#82ca9d" />
                    <Line type="monotone" dataKey="physics_loss" stroke="#ffc658" />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Models Tab */}
          <TabsContent value="models">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Card>
                <CardHeader>
                  <CardTitle>Model Performance</CardTitle>
                  <CardDescription>Key metrics for current model</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={mockModelMetrics}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="metric" />
                      <YAxis domain={[0, 1]} />
                      <Tooltip />
                      <Bar dataKey="value" fill="#8884d8" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Model Versions</CardTitle>
                  <CardDescription>Available model versions</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="p-3 bg-accent rounded-lg">
                      <div className="font-semibold">PINN v1.0</div>
                      <div className="text-sm text-muted-foreground">Fidelity: 95% | Status: Active</div>
                    </div>
                    <div className="p-3 bg-accent rounded-lg">
                      <div className="font-semibold">PINO v1.0</div>
                      <div className="text-sm text-muted-foreground">Fidelity: 92% | Status: Staging</div>
                    </div>
                    <div className="p-3 bg-accent rounded-lg">
                      <div className="font-semibold">PINN v0.9</div>
                      <div className="text-sm text-muted-foreground">Fidelity: 88% | Status: Archived</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Analytics Tab */}
          <TabsContent value="analytics">
            <Card>
              <CardHeader>
                <CardTitle>PINN vs CFD Comparison</CardTitle>
                <CardDescription>Prediction accuracy across domain</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={400}>
                  <LineChart data={mockPredictionComparison}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="x" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="pinn" stroke="#8884d8" name="PINN Prediction" />
                    <Line type="monotone" dataKey="cfd" stroke="#82ca9d" name="CFD Reference" />
                    <Line type="monotone" dataKey="error" stroke="#ffc658" name="Absolute Error" />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
