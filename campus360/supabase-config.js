// Supabase Configuration
const SUPABASE_URL = "https://cryibpyowmikgsiijeyd.supabase.co";
const SUPABASE_ANON_KEY = "sb_publishable_O4A1KkLr8NbZE7wo8hHVug_kKtXMM5N";

// Initialize Supabase Client
const client = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

window.supabase = client;
console.log("Supabase Client Initialized");
