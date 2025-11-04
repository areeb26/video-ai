import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Character API
export const characterApi = {
  getAll: () => api.get('/characters'),
  getOne: (id: number) => api.get(`/characters/${id}`),
  create: (data: any) => api.post('/characters', data),
  update: (id: number, data: any) => api.put(`/characters/${id}`, data),
  delete: (id: number) => api.delete(`/characters/${id}`),
  uploadFaceReference: (id: number, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post(`/characters/${id}/face-references`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  createOutfit: (id: number, data: any) => api.post(`/characters/${id}/outfits`, data),
  getOutfits: (id: number) => api.get(`/characters/${id}/outfits`),
};

// Project API
export const projectApi = {
  getAll: () => api.get('/projects'),
  getOne: (id: number) => api.get(`/projects/${id}`),
  create: (data: any) => api.post('/projects', data),
  update: (id: number, data: any) => api.put(`/projects/${id}`, data),
  delete: (id: number) => api.delete(`/projects/${id}`),

  // Beats
  createBeat: (projectId: number, data: any) => api.post(`/projects/${projectId}/beats`, data),
  getBeats: (projectId: number) => api.get(`/projects/${projectId}/beats`),
  updateBeat: (beatId: number, data: any) => api.put(`/projects/beats/${beatId}`, data),

  // Shots
  createShot: (beatId: number, data: any) => api.post(`/projects/beats/${beatId}/shots`, data),
  getShots: (beatId: number) => api.get(`/projects/beats/${beatId}/shots`),
  updateShot: (shotId: number, data: any) => api.put(`/projects/shots/${shotId}`, data),
};

// Generation API
export const generationApi = {
  create: (data: any) => api.post('/generation', data),
  getAll: (params?: any) => api.get('/generation', { params }),
  getOne: (id: number) => api.get(`/generation/${id}`),
  validateContinuity: (id: number) => api.post(`/generation/${id}/validate-continuity`),
  generateForShot: (shotId: number, quality: string = 'low') =>
    api.post(`/generation/shots/${shotId}/generate`, null, { params: { quality } }),
};
