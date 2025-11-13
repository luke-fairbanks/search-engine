import axios from 'axios';
import { SearchResponse, IndexStats } from '../types/SearchTypes';

const API_BASE_URL = process.env.REACT_APP_API_URL || '/api';

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
  }
};
