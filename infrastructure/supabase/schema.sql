-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table for simulation jobs
CREATE TABLE IF NOT EXISTS simulations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id INT REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    parameters JSONB NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    result_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table for model predictions (caching)
CREATE TABLE IF NOT EXISTS predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    input_params JSONB NOT NULL,
    prediction_mean JSONB NOT NULL,
    prediction_std JSONB,
    model_version VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE (input_params)
);

-- Table for model versions
CREATE TABLE IF NOT EXISTS model_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_id VARCHAR(255) NOT NULL,
    version VARCHAR(50) NOT NULL,
    model_path TEXT NOT NULL,
    onnx_path TEXT,
    config JSONB,
    metrics JSONB,
    training_data_hash VARCHAR(255),
    model_hash VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE (model_id, version)
);

-- Table for ethics validation logs
CREATE TABLE IF NOT EXISTS ethics_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    simulation_id UUID REFERENCES simulations(id),
    violations JSONB,
    ethics_score FLOAT,
    is_ethical BOOLEAN,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table for training jobs
CREATE TABLE IF NOT EXISTS training_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id INT REFERENCES users(id),
    model_id VARCHAR(255) NOT NULL,
    dataset_path TEXT,
    config JSONB,
    status VARCHAR(50) DEFAULT 'pending',
    progress FLOAT DEFAULT 0,
    metrics JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_predictions_input_params ON predictions USING GIN (input_params);
CREATE INDEX IF NOT EXISTS idx_simulations_user_id ON simulations(user_id);
CREATE INDEX IF NOT EXISTS idx_model_versions_model_id ON model_versions(model_id);
CREATE INDEX IF NOT EXISTS idx_ethics_logs_simulation_id ON ethics_logs(simulation_id);
CREATE INDEX IF NOT EXISTS idx_training_jobs_user_id ON training_jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_training_jobs_status ON training_jobs(status);
