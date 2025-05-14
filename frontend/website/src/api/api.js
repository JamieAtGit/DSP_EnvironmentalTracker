const BASE_URL = import.meta.env.VITE_API_BASE_URL;

export async function fetchEcoData() {
  const res = await fetch(`${BASE_URL}/api/eco-data`);
  if (!res.ok) throw new Error('Failed to fetch eco data');
  return res.json();
}

export async function fetchInsights() {
  const res = await fetch(`${BASE_URL}/insights`);
  if (!res.ok) throw new Error('Failed to fetch insights');
  return res.json();
}
