import request from './index'

export interface Pet {
  id: string
  user_id: string
  name: string
  species: string
  breed: string
  age: string
  weight: string
  gender: string
  birthday: string
  notes: string
  created_at: string
  updated_at: string
}

export interface CreatePetRequest {
  name: string
  species?: string
  breed?: string
  age?: string
  weight?: string
  gender?: string
  birthday?: string
  notes?: string
}

export interface UpdatePetRequest {
  name?: string
  species?: string
  breed?: string
  age?: string
  weight?: string
  gender?: string
  birthday?: string
  notes?: string
}

export const petsApi = {
  list() {
    return request.get<any, Pet[]>('/pets')
  },

  get(id: string) {
    return request.get<any, Pet>(`/pets/${id}`)
  },

  create(data: CreatePetRequest) {
    return request.post<any, Pet>('/pets', data)
  },

  update(id: string, data: UpdatePetRequest) {
    return request.put<any, Pet>(`/pets/${id}`, data)
  },

  delete(id: string) {
    return request.delete<any, { message: string }>(`/pets/${id}`)
  }
}
