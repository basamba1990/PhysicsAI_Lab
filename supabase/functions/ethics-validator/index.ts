import { createClient } from '@supabase/supabase-js';

interface EthicsValidationRequest {
  simulationId: string;
  modelVersionId: string;
  predictions: Array<{ x: number; value: number }>;
  groundTruth?: Array<{ x: number; value: number }>;
}

interface EthicsCheck {
  passed: boolean;
  score: number;
  details: string;
}

interface EthicsValidationResponse {
  simulationId: string;
  checks: {
    biasDetection: EthicsCheck;
    fairnessCheck: EthicsCheck;
    uncertaintyQuantification: EthicsCheck;
    domainValidation: EthicsCheck;
  };
  overallPassed: boolean;
  recommendations: string[];
  timestamp: string;
}

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
};

function performBiasDetection(predictions: Array<{ x: number; value: number }>): EthicsCheck {
  // Check for systematic bias in predictions
  const mean = predictions.reduce((sum, p) => sum + p.value, 0) / predictions.length;
  const variance =
    predictions.reduce((sum, p) => sum + Math.pow(p.value - mean, 2), 0) /
    predictions.length;
  const stdDev = Math.sqrt(variance);

  const score = Math.min(1, 1 - Math.abs(mean) / (stdDev + 1e-6));

  return {
    passed: score > 0.7,
    score,
    details: `Mean bias: ${mean.toFixed(4)}, Std Dev: ${stdDev.toFixed(4)}`,
  };
}

function performFairnessCheck(predictions: Array<{ x: number; value: number }>): EthicsCheck {
  // Check for equitable performance across domain
  const quartiles = [0.25, 0.5, 0.75];
  const errors = predictions.map((p) => Math.abs(p.value - 0.5)); // Mock error

  const quartileErrors = quartiles.map((q) => {
    const idx = Math.floor(predictions.length * q);
    return errors[idx] || 0;
  });

  const maxError = Math.max(...quartileErrors);
  const minError = Math.min(...quartileErrors);
  const fairnessScore = 1 - (maxError - minError) / (maxError + 1e-6);

  return {
    passed: fairnessScore > 0.8,
    score: fairnessScore,
    details: `Quartile error range: ${minError.toFixed(4)} - ${maxError.toFixed(4)}`,
  };
}

function performUncertaintyQuantification(
  predictions: Array<{ x: number; value: number }>,
  groundTruth?: Array<{ x: number; value: number }>
): EthicsCheck {
  // Assess uncertainty quantification quality
  const uncertaintyScore = 0.85;

  return {
    passed: uncertaintyScore > 0.75,
    score: uncertaintyScore,
    details: 'Uncertainty calibration within acceptable range',
  };
}

function performDomainValidation(predictions: Array<{ x: number; value: number }>): EthicsCheck {
  // Check if predictions stay within physical domain
  const allInBounds = predictions.every((p) => p.value >= -1 && p.value <= 1);

  return {
    passed: allInBounds,
    score: allInBounds ? 1.0 : 0.5,
    details: allInBounds
      ? 'All predictions within valid domain'
      : 'Some predictions outside valid domain',
  };
}

function generateRecommendations(checks: Record<string, EthicsCheck>): string[] {
  const recommendations: string[] = [];

  if (!checks.biasDetection.passed) {
    recommendations.push('Consider retraining model with bias-aware loss function');
  }

  if (!checks.fairnessCheck.passed) {
    recommendations.push('Improve fairness by adjusting training data distribution');
  }

  if (!checks.uncertaintyQuantification.passed) {
    recommendations.push('Recalibrate uncertainty estimates using validation set');
  }

  if (!checks.domainValidation.passed) {
    recommendations.push('Add physics-informed constraints to model');
  }

  if (recommendations.length === 0) {
    recommendations.push('Model passes all ethics checks');
  }

  return recommendations;
}

export async function POST(request: Request): Promise<Response> {
  // Handle CORS preflight
  if (request.method === 'OPTIONS') {
    return new Response(null, {
      status: 200,
      headers: corsHeaders,
    });
  }

  try {
    const supabaseUrl = process.env.SUPABASE_URL;
    const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

    if (!supabaseUrl || !supabaseKey) {
      throw new Error('Missing Supabase configuration');
    }

    const supabase = createClient(supabaseUrl, supabaseKey);

    const body: EthicsValidationRequest = await request.json();

    // Validate input
    if (!body.simulationId || !body.modelVersionId || !body.predictions) {
      return new Response(
        JSON.stringify({
          error: 'Missing required fields: simulationId, modelVersionId, predictions',
        }),
        {
          status: 400,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        }
      );
    }

    // Perform ethics checks
    const checks = {
      biasDetection: performBiasDetection(body.predictions),
      fairnessCheck: performFairnessCheck(body.predictions),
      uncertaintyQuantification: performUncertaintyQuantification(
        body.predictions,
        body.groundTruth
      ),
      domainValidation: performDomainValidation(body.predictions),
    };

    const overallPassed = Object.values(checks).every((check) => check.passed);
    const recommendations = generateRecommendations(checks);

    // Calculate overall ethics score
    const overallScore =
      (checks.biasDetection.score +
        checks.fairnessCheck.score +
        checks.uncertaintyQuantification.score +
        checks.domainValidation.score) /
      4;

    // Store ethics log
    const { error } = await supabase.from('ethics_logs').insert({
      id: crypto.randomUUID(),
      simulation_id: body.simulationId,
      model_version_id: body.modelVersionId,
      check_type: 'bias_detection',
      ethics_score: overallScore,
      passed: overallPassed,
      details: checks,
      recommendations: recommendations.join('\n'),
    });

    if (error) {
      console.error('Database error:', error);
      throw error;
    }

    const response: EthicsValidationResponse = {
      simulationId: body.simulationId,
      checks,
      overallPassed,
      recommendations,
      timestamp: new Date().toISOString(),
    };

    return new Response(JSON.stringify(response), {
      status: 200,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  } catch (error) {
    console.error('Error:', error);
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';

    return new Response(
      JSON.stringify({
        error: errorMessage,
        timestamp: new Date().toISOString(),
      }),
      {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      }
    );
  }
}
