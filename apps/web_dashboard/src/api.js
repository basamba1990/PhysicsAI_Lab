import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL || 'http://localhost:54321',
  import.meta.env.VITE_SUPABASE_ANON_KEY || 'your-anon-key'
)

export async function invokeEdgeFunction(name, payload) {
  const { data, error } = await supabase.functions.invoke(name, {
    body: payload,
  })
  if (error) throw error
  return data
}
