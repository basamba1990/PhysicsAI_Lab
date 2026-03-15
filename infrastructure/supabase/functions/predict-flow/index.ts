import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.39.0"
import { loadOnnxModel, runInferenceWithUQ, runInferenceWithoutUQ } from "./onnx_inference.ts"

interface PredictionInput {
  x: number
  t: number
  model_version?: string
  uncertainty_quantification?: boolean
  n_samples?: number
}

interface PredictionOutput {
  u: number
  uncertainty?: number
  confidence?: number
  model_version: string
  cached: boolean
  timestamp: string
}

// Cache en mémoire pour les prédictions (optionnel, pour performance)
const predictionCache = new Map<string, PredictionOutput>()

// Charger le modèle ONNX au démarrage
let onnxModel: any = null
let modelLoadError: Error | null = null

async function initializeModel() {
  try {
    const modelPath = Deno.env.get("ONNX_MODEL_PATH") || "https://storage.supabase.co/models/pinn_model.onnx"
    onnxModel = await loadOnnxModel(modelPath)
    console.log("[INIT] Modèle ONNX chargé avec succès")
  } catch (error) {
    modelLoadError = error as Error
    console.error("[INIT] Erreur lors du chargement du modèle:", modelLoadError.message)
  }
}

// Initialiser le modèle au démarrage
initializeModel()

serve(async (req) => {
  // Gérer les requêtes CORS preflight
  if (req.method === "OPTIONS") {
    return new Response("ok", {
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST",
        "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type"
      }
    })
  }

  // Accepter uniquement POST
  if (req.method !== "POST") {
    return new Response(JSON.stringify({ error: "Method not allowed" }), {
      status: 405,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    })
  }

  try {
    // Parser l'input
    const input: PredictionInput = await req.json()
    
    // Valider les inputs
    if (typeof input.x !== "number" || typeof input.t !== "number") {
      throw new Error("Invalid input: x and t must be numbers")
    }

    // Vérifier que le modèle est chargé
    if (!onnxModel) {
      throw new Error("Model not loaded: " + (modelLoadError?.message || "Unknown error"))
    }

    // Générer une clé de cache
    const cacheKey = `${input.x},${input.t},${input.model_version || "default"}`
    
    // Vérifier le cache en mémoire
    if (predictionCache.has(cacheKey)) {
      const cached = predictionCache.get(cacheKey)!
      cached.cached = true
      return new Response(JSON.stringify(cached), {
        headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
        status: 200
      })
    }

    // Effectuer l'inférence
    const useUQ = input.uncertainty_quantification ?? true
    const nSamples = input.n_samples ?? 100
    
    let inferenceResult: any
    
    if (useUQ) {
      // Inférence avec quantification d'incertitude (Monte Carlo Dropout)
      inferenceResult = await runInferenceWithUQ(onnxModel, { x: input.x, t: input.t }, nSamples)
    } else {
      // Inférence simple sans UQ
      inferenceResult = await runInferenceWithoutUQ(onnxModel, { x: input.x, t: input.t })
    }

    // Construire la réponse
    const prediction: PredictionOutput = {
      u: inferenceResult.mean,
      uncertainty: inferenceResult.std,
      confidence: Math.max(0, Math.min(1, 1 - (inferenceResult.std || 0))),
      model_version: input.model_version || "default_pinn_v1",
      cached: false,
      timestamp: new Date().toISOString()
    }

    // Sauvegarder en cache mémoire
    predictionCache.set(cacheKey, prediction)

    // Optionnel: Sauvegarder en Supabase pour traçabilité
    const supabaseUrl = Deno.env.get("SUPABASE_URL")
    const supabaseKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")

    if (supabaseUrl && supabaseKey) {
      try {
        const supabaseClient = createClient(supabaseUrl, supabaseKey)
        
        // Upsert dans la table predictions
        const { error } = await supabaseClient
          .from("predictions")
          .upsert({
            input_params: { x: input.x, t: input.t },
            prediction_mean: { u: prediction.u },
            prediction_std: { u: prediction.uncertainty },
            model_version: prediction.model_version,
            created_at: prediction.timestamp
          }, { 
            onConflict: 'input_params'
          })

        if (error) {
          console.warn("[DB] Erreur lors de l'upsert Supabase:", error.message)
        } else {
          console.log("[DB] Prédiction sauvegardée en Supabase")
        }
      } catch (dbError) {
        console.warn("[DB] Erreur lors de la sauvegarde:", dbError)
      }
    }

    return new Response(JSON.stringify(prediction), {
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
      status: 200
    })
  } catch (err) {
    const errorMessage = err instanceof Error ? err.message : "Unknown error"
    console.error("[ERROR]", errorMessage)
    
    return new Response(JSON.stringify({ 
      error: errorMessage,
      timestamp: new Date().toISOString()
    }), {
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
      status: 400
    })
  }
})
