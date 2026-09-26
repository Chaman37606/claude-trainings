async function postJSON(url, body){
  const res = await fetch(url, {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify(body)
  });
  return res.json();
}

document.getElementById('calc').addEventListener('click', async ()=>{
  const amount = Number(document.getElementById('amount').value);
  const rate = Number(document.getElementById('rate').value);
  const years = Number(document.getElementById('years').value);
  const data = await postJSON('/api/calc', { amount, rate, years });
  const fv = data.futureValue;
  const invested = data.totalInvested;
  const gains = data.gains;
  document.getElementById('result').textContent = `Future value: ₹${fv ? fv.toFixed(2) : 'error'} | Invested: ₹${invested ? invested.toFixed(2) : 'error'} | Gains: ₹${gains ? gains.toFixed(2) : 'error'}`;
});

document.getElementById('calcAgent').addEventListener('click', async ()=>{
  const amount = Number(document.getElementById('amount').value);
  const rate = Number(document.getElementById('rate').value);
  const years = Number(document.getElementById('years').value);
  try {
    const data = await postJSON('/api/calc-with-agent', { amount, rate, years });
    const fv = data.futureValue;
    const invested = data.totalInvested;
    const gains = data.gains;
    document.getElementById('result').textContent = `[Agent] Future value: ₹${fv ? fv.toFixed(2) : 'error'} | Invested: ₹${invested ? invested.toFixed(2) : 'error'} | Gains: ₹${gains ? gains.toFixed(2) : 'error'}`;
  } catch(e) {
    document.getElementById('result').textContent = `Error: ${e.message}`;
  }
});

document.getElementById('fetchNav').addEventListener('click', async ()=>{
  const id = document.getElementById('fundId').value.trim();
  if (!id) { document.getElementById('navResult').textContent = 'Enter fund id'; return; }
  try{
    const res = await fetch(`/api/nav/${encodeURIComponent(id)}`);
    const json = await res.json();
    document.getElementById('navResult').textContent = JSON.stringify(json, null, 2);
  }catch(e){
    document.getElementById('navResult').textContent = e.message;
  }
});
