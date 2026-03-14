import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.39.0"

interface PredictionInput {
  x: number;
  t: number;
}

serve(async (req) => {
  // Handle CORS preflight
  if (req.method === "OPTIONS") {
    return new Response("ok", { 
      headers: { 
        "Access-Control-Allow-Origin": "*", 
        "Access-Control-Allow-Methods": "POST", 
        "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type" 
      } 
    })
  }

  // Only allow POST
  if (req.method !== "POST") {
    return new Response(JSON.stringify({ error: "Method not allowed" }), { 
      status: 405, 
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" } 
    })
  }

  try {
    const { x, t }: PredictionInput = await req.json()
    if (typeof x !== "number" || typeof t !== "number") {
      throw new Error("Invalid input: x and t must be numbers")
    }

    // Inference placeholder
    const u = Math.sin(x) * Math.cos(t)

    // Optional: Store in Supabase for caching
    const supabaseUrl = Deno.env.get("SUPABASE_URL")
    const supabaseKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")

    if (supabaseUrl && supabaseKey) {
      const supabaseClient = createClient(supabaseUrl, supabaseKey)
      await supabaseClient.from("predictions").upsert({
        input_hash: `${x},${t}`,
        output: { u },
        confidence: 0.95
      }, { onConflict: 'input_hash' })
    }

    return new Response(JSON.stringify({ u, confidence: "high" }), {
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
      status: 200
    })
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), {
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
      status: 400
    })
  }
})
