import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 10 },
    { duration: '1m',  target: 20 },
    { duration: '30s', target: 0 },
  ],
};

const URL = 'http://iris.iris.svc.cluster.local/predict';
const HEADERS = { headers: { 'Content-Type': 'application/json' } };
const SAMPLES = [
  { sepal_length: 5.1, sepal_width: 3.5, petal_length: 1.4, petal_width: 0.2 }, // setosa
  { sepal_length: 6.0, sepal_width: 2.7, petal_length: 5.1, petal_width: 1.6 }, // versicolor
  { sepal_length: 6.9, sepal_width: 3.1, petal_length: 5.4, petal_width: 2.1 }, // virginica
];

export default function () {
  // ~10% invalid requests so the 4xx line shows up on the dashboard
  const body = Math.random() < 0.1
    ? { sepal_length: -1, sepal_width: 3.5, petal_length: 1.4, petal_width: 0.2 }
    : SAMPLES[Math.floor(Math.random() * SAMPLES.length)];
  const res = http.post(URL, JSON.stringify(body), HEADERS);
  check(res, { 'status is 200 or 422': (r) => r.status === 200 || r.status === 422 });
  sleep(0.2);
}
