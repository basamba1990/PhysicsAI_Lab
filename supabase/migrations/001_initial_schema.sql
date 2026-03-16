-- Physics AI Lab - PostgreSQL Schema for Supabase
-- Complete schema with tables, indexes, views, and RLS policies

-- ============================================================================
-- TABLES
-- ============================================================================

-- Simulations table
CREATE TABLE IF NOT EXISTS public.simulations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  simulation_type VARCHAR(50) NOT NULL CHECK (simulation_type IN ('heat_transfer', 'fluid_dynamics', 'wave_propagation', 'custom')),
  parameters JSONB NOT NULL,
  status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed')),
  progress DECIMAL(5,2) DEFAULT 0,
  result_url VARCHAR(512),
  model_version_id UUID,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  completed_at TIMESTAMP WITH TIME ZONE,
  CONSTRAINT progress_range CHECK (progress >= 0 AND progress <= 100)
);

-- Predictions table
CREATE TABLE IF NOT EXISTS public.predictions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  simulation_id UUID NOT NULL REFERENCES public.simulations(id) ON DELETE CASCADE,
  model_version_id UUID NOT NULL,
  prediction_data JSONB NOT NULL,
  accuracy DECIMAL(5,4),
  error_metrics JSONB,
  compute_time INTEGER,
  cached_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Model versions table
CREATE TABLE IF NOT EXISTS public.model_versions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  version VARCHAR(50) NOT NULL,
  model_type VARCHAR(50) NOT NULL CHECK (model_type IN ('pinn', 'pino', 'hybrid')),
  onnx_url VARCHAR(512),
  metrics JSONB,
  is_active BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Training jobs table
CREATE TABLE IF NOT EXISTS public.training_jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  model_version_id UUID NOT NULL REFERENCES public.model_versions(id) ON DELETE CASCADE,
  status VARCHAR(50) DEFAULT 'queued' CHECK (status IN ('queued', 'running', 'completed', 'failed')),
  progress DECIMAL(5,2) DEFAULT 0,
  epochs INTEGER,
  current_epoch INTEGER DEFAULT 0,
  batch_size INTEGER,
  learning_rate DECIMAL(10,8),
  training_metrics JSONB,
  error_message TEXT,
  started_at TIMESTAMP WITH TIME ZONE,
  completed_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  CONSTRAINT progress_range CHECK (progress >= 0 AND progress <= 100)
);

-- Ethics logs table
CREATE TABLE IF NOT EXISTS public.ethics_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  simulation_id UUID NOT NULL REFERENCES public.simulations(id) ON DELETE CASCADE,
  model_version_id UUID NOT NULL,
  check_type VARCHAR(50) NOT NULL CHECK (check_type IN ('bias_detection', 'fairness_check', 'uncertainty_quantification', 'domain_validation')),
  ethics_score DECIMAL(5,4),
  passed BOOLEAN NOT NULL,
  details JSONB,
  recommendations TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- INDEXES
-- ============================================================================

CREATE INDEX idx_simulations_user_id ON public.simulations(user_id);
CREATE INDEX idx_simulations_status ON public.simulations(status);
CREATE INDEX idx_simulations_created_at ON public.simulations(created_at DESC);

CREATE INDEX idx_predictions_simulation_id ON public.predictions(simulation_id);
CREATE INDEX idx_predictions_model_version_id ON public.predictions(model_version_id);
CREATE INDEX idx_predictions_created_at ON public.predictions(cached_at DESC);

CREATE INDEX idx_model_versions_user_id ON public.model_versions(user_id);
CREATE INDEX idx_model_versions_is_active ON public.model_versions(is_active);
CREATE INDEX idx_model_versions_created_at ON public.model_versions(created_at DESC);

CREATE INDEX idx_training_jobs_user_id ON public.training_jobs(user_id);
CREATE INDEX idx_training_jobs_status ON public.training_jobs(status);
CREATE INDEX idx_training_jobs_completed_at ON public.training_jobs(completed_at DESC);

CREATE INDEX idx_ethics_logs_simulation_id ON public.ethics_logs(simulation_id);
CREATE INDEX idx_ethics_logs_model_version_id ON public.ethics_logs(model_version_id);
CREATE INDEX idx_ethics_logs_ethics_score ON public.ethics_logs(ethics_score);

-- ============================================================================
-- VIEWS
-- ============================================================================

-- Simulation statistics view
CREATE OR REPLACE VIEW public.simulation_stats AS
SELECT 
  COUNT(*) as total_simulations,
  COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
  COUNT(CASE WHEN status = 'running' THEN 1 END) as running,
  COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed,
  AVG(CASE WHEN status = 'completed' THEN (parameters->>'fidelity')::DECIMAL ELSE NULL END) as avg_fidelity
FROM public.simulations;

-- Model performance view
CREATE OR REPLACE VIEW public.model_performance AS
SELECT 
  model_versions.id as model_id,
  model_versions.name as model_name,
  model_versions.version,
  model_versions.model_type,
  (model_versions.metrics->>'accuracy')::DECIMAL as accuracy,
  (model_versions.metrics->>'loss')::DECIMAL as loss,
  (model_versions.metrics->>'fidelity')::DECIMAL as fidelity,
  model_versions.created_at,
  model_versions.is_active
FROM public.model_versions
ORDER BY model_versions.created_at DESC;

-- User simulations summary view
CREATE OR REPLACE VIEW public.user_simulations_summary AS
SELECT 
  s.user_id,
  COUNT(*) as total_simulations,
  COUNT(CASE WHEN s.status = 'completed' THEN 1 END) as completed_simulations,
  COUNT(CASE WHEN s.status = 'running' THEN 1 END) as running_simulations,
  AVG(CASE WHEN s.status = 'completed' THEN (s.parameters->>'fidelity')::DECIMAL ELSE NULL END) as avg_fidelity
FROM public.simulations s
GROUP BY s.user_id;

-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE public.simulations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.model_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.training_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ethics_logs ENABLE ROW LEVEL SECURITY;

-- Simulations RLS policies
CREATE POLICY "Users can view their own simulations"
  ON public.simulations FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create simulations"
  ON public.simulations FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own simulations"
  ON public.simulations FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own simulations"
  ON public.simulations FOR DELETE
  USING (auth.uid() = user_id);

-- Model versions RLS policies
CREATE POLICY "Users can view their own models"
  ON public.model_versions FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create models"
  ON public.model_versions FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own models"
  ON public.model_versions FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own models"
  ON public.model_versions FOR DELETE
  USING (auth.uid() = user_id);

-- Training jobs RLS policies
CREATE POLICY "Users can view their own training jobs"
  ON public.training_jobs FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create training jobs"
  ON public.training_jobs FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own training jobs"
  ON public.training_jobs FOR UPDATE
  USING (auth.uid() = user_id);

-- Predictions RLS (through simulations)
CREATE POLICY "Users can view predictions from their simulations"
  ON public.predictions FOR SELECT
  USING (
    simulation_id IN (
      SELECT id FROM public.simulations WHERE user_id = auth.uid()
    )
  );

-- Ethics logs RLS (through simulations)
CREATE POLICY "Users can view ethics logs from their simulations"
  ON public.ethics_logs FOR SELECT
  USING (
    simulation_id IN (
      SELECT id FROM public.simulations WHERE user_id = auth.uid()
    )
  );

-- ============================================================================
-- STORAGE BUCKETS
-- ============================================================================

-- Create storage buckets for models and datasets
INSERT INTO storage.buckets (id, name, public)
VALUES 
  ('models', 'models', true),
  ('datasets', 'datasets', true),
  ('results', 'results', true)
ON CONFLICT (id) DO NOTHING;

-- Storage RLS policies
CREATE POLICY "Users can upload models"
  ON storage.objects FOR INSERT
  WITH CHECK (
    bucket_id = 'models' AND
    auth.uid()::text = (storage.foldername(name))[1]
  );

CREATE POLICY "Users can view models"
  ON storage.objects FOR SELECT
  USING (bucket_id = 'models');
