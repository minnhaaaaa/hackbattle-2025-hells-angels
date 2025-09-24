import axios from 'axios';

const BASE_URL = "http://127.0.0.1:8000"; 

export const getMockSMS = async () => {
  const response = await axios.get(`${BASE_URL}/mock-sms`);
  return response.data.transactions;
};

export const getCategorizedTransactions = async () => {
  const response = await axios.get(`${BASE_URL}/categorize`);
  return response.data.categorized_transactions;
};

export const getForecast = async () => {
  const response = await axios.get(`${BASE_URL}/forecast`);
  return response.data.forecast;
};

export const getFinancialTips = async (category) => {
  const response = await axios.get(`${BASE_URL}/financial-tip/${category}`);
  return response.data.tips;
};

export const getFraudulentTransactions = async () => {
  const response = await axios.get(`${BASE_URL}/fraud`);
  return response.data.fraud_transactions;
};

export const getIdentityFingerprint = async () => {
  const response = await axios.get(`${BASE_URL}/fingerprint`);
  return response.data.fingerprint;
};
