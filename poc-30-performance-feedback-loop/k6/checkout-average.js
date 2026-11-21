import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  "stages": [
    {
      "duration": "5m",
      "target": 50
    },
    {
      "duration": "30m",
      "target": 50
    },
    {
      "duration": "5m",
      "target": 0
    }
  ],
  "thresholds": {
    "http_req_failed": [
      "rate<0.001"
    ],
    "http_req_duration": [
      "p(95)<300"
    ]
  }
};

export function setup() {
  return { product: 'OLJCESPC7Z' };
}

export default function (data) {
  const res = http.get(`http://frontend-proxy:8080/api/products/${data.product}`);
  check(res, { 'status is 200': (r) => r.status === 200 });
  sleep(1);
}
