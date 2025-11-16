import axios from 'axios';
import { SearchResponse, IndexStats } from '../types/SearchTypes';

const API_BASE_URL = process.env.REACT_APP_API_URL + "/api" || 'http://localhost:5001/api';
console.log("API_BASE_URL:", API_BASE_URL);

// to update git
export const searchApi = {
  search: async (query: string, k: number = 10, alpha: number = 0.2, beta: number = 0.8): Promise<SearchResponse> => {
    const response = await axios.get(`${API_BASE_URL}/search`, {
      params: { q: query, alpha, beta, k }
    });
    return response.data;
  },

  getStats: async (): Promise<IndexStats> => {
    const response = await axios.get(`${API_BASE_URL}/stats`);
    return response.data;
  },

  getSuggestions: async (query: string, limit: number = 8): Promise<string[]> => {
    if (!query || query.length < 2) {
      return [];
    }
    const response = await axios.get(`${API_BASE_URL}/suggest`, {
      params: { q: query, limit }
    });
    return response.data.suggestions || [];
  }
};
