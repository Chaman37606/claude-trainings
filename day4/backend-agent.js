const Anthropic = require('@anthropic-ai/sdk');
const mcp = require('./mcp_client');

const client = new Anthropic.default();

async function calculateSIPWithAgent(amount, rate, years) {
  const prompt = `Calculate SIP (Systematic Investment Plan) returns with these parameters:
- Monthly Investment: ₹${amount}
- Annual Return Rate: ${rate}%
- Investment Period: ${years} years

Provide the calculation in JSON format with:
- futureValue: final amount
- totalInvested: total amount invested
- gains: profit earned`;

  const message = await client.messages.create({
    model: 'claude-opus-5',
    max_tokens: 200,
    messages: [
      {
        role: 'user',
        content: prompt,
      },
    ],
  });

  const responseText = message.content[0].type === 'text' ? message.content[0].text : '';
  try {
    const jsonMatch = responseText.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      return JSON.parse(jsonMatch[0]);
    }
  } catch (e) {
    console.error('Failed to parse agent response:', e);
  }

  return null;
}

async function fetchAndAnalyzeNAV(fundId) {
  const navData = await mcp.fetchNav(fundId);

  const prompt = `Analyze this mutual fund NAV data:
Fund: ${navData.schemeName}
Latest NAV: ${navData.latest?.nav || 'N/A'}
Date: ${navData.latest?.date || 'N/A'}

Provide a brief analysis in JSON format.`;

  const message = await client.messages.create({
    model: 'claude-opus-5',
    max_tokens: 200,
    messages: [
      {
        role: 'user',
        content: prompt,
      },
    ],
  });

  return {
    navData,
    analysis: message.content[0].type === 'text' ? message.content[0].text : '',
  };
}

module.exports = { calculateSIPWithAgent, fetchAndAnalyzeNAV };
