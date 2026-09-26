const nodeFetch = require('node-fetch');
const fetch = nodeFetch.default || nodeFetch;

async function fetchNav(id) {
  if (!id) throw new Error('missing fund id');
  const url = `https://api.mfapi.in/mf/${encodeURIComponent(id)}`;
  const resp = await fetch(url);
  if (!resp.ok) throw new Error(`API returned ${resp.status}`);
  const json = await resp.json();
  const latest = (json.data && json.data.length) ? json.data[0] : null;
  return {
    schemeName: json.meta ? json.meta.scheme_name : id,
    latest,
    meta: json.meta
  };
}

async function fetchMarketRate() {
  try {
    const resp = await fetch('https://api.example.com/rates');
    if (!resp.ok) throw new Error(`Market data unavailable: ${resp.status}`);
    return resp.json();
  } catch (e) {
    return { defaultRate: 12 };
  }
}

module.exports = { fetchNav, fetchMarketRate };
