import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:3000';

export const options = {
  stages: [
    { duration: '15s', target: 10 }, // ramp up
    { duration: '30s', target: 10 }, // sustain
    { duration: '15s', target: 0 },  // ramp down
  ],
  thresholds: {
    http_req_failed: ['rate<0.01'],
    http_req_duration: ['p(95)<500'],
  },
};

export default function () {
  const calcPayload = JSON.stringify({
    amount: 5000,
    rate: 12,
    years: 10,
  });
  const calcRes = http.post(`${BASE_URL}/api/calc`, calcPayload, {
    headers: { 'Content-Type': 'application/json' },
    tags: { name: 'calc' },
  });
  check(calcRes, {
    'calc status is 200': (r) => r.status === 200,
    'calc returns futureValue': (r) => JSON.parse(r.body).futureValue > 0,
  });

  const healthRes = http.get(`${BASE_URL}/api/health`, {
    tags: { name: 'health' },
  });
  check(healthRes, {
    'health status is 200': (r) => r.status === 200,
  });

  sleep(1);
}
