const express = require('express');
const path = require('path');
const cors = require('cors');
const mcp = require('./mcp_client');

const app = express();
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

function calculateSIP(amount, rate, years) {
  const P = parseFloat(amount);
  const monthlyRate = parseFloat(rate) / 100 / 12;
  const n = parseInt(years) * 12;
  const totalInvested = P * n;

  if (monthlyRate === 0) {
    return { futureValue: totalInvested, totalInvested, gains: 0 };
  }

  const fv = P * ((Math.pow(1 + monthlyRate, n) - 1) / monthlyRate) * (1 + monthlyRate);
  const gains = fv - totalInvested;
  return { futureValue: fv, totalInvested, gains };
}

app.post('/api/calc', (req, res) => {
  const { amount, rate, years } = req.body;
  if (amount == null || rate == null || years == null) {
    return res.status(400).json({ error: 'amount, rate and years are required' });
  }

  try {
    const result = calculateSIP(amount, rate, years);
    res.json(result);
  } catch (e) {
    res.status(400).json({ error: e.message });
  }
});

app.post('/api/calc-with-agent', async (req, res) => {
  const { amount, rate, years } = req.body;
  if (amount == null || rate == null || years == null) {
    return res.status(400).json({ error: 'amount, rate and years are required' });
  }

  try {
    const result = calculateSIP(amount, rate, years);
    res.json({ ...result, calculatedBy: 'agent-backend' });
  } catch (e) {
    res.status(400).json({ error: e.message });
  }
});

app.get('/api/nav/:id', async (req, res) => {
  try {
    const id = req.params.id;
    const data = await mcp.fetchNav(id);
    res.json({ data });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', service: 'SIP Calculator Backend' });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server started on http://localhost:${PORT}`));
