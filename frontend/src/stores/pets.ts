import { defineStore } from 'pinia'
import { ref } from 'vue'
import { petsApi, type Pet, type CreatePetRequest, type UpdatePetRequest } from '@/api/pets'

export const usePetsStore = defineStore('pets', () => {
  const pets = ref<Pet[]>([])
  const currentPet = ref<Pet | null>(null)

  async function fetchPets() {
    pets.value = await petsApi.list()
  }

  async function createPet(data: CreatePetRequest) {
    const pet = await petsApi.create(data)
    pets.value.unshift(pet)
    return pet
  }

  async function updatePet(id: string, data: UpdatePetRequest) {
    const pet = await petsApi.update(id, data)
    const index = pets.value.findIndex(p => p.id === id)
    if (index !== -1) {
      pets.value[index] = pet
    }
    if (currentPet.value?.id === id) {
      currentPet.value = pet
    }
    return pet
  }

  async function deletePet(id: string) {
    await petsApi.delete(id)
    pets.value = pets.value.filter(p => p.id !== id)
    if (currentPet.value?.id === id) {
      currentPet.value = null
    }
  }

  function setCurrentPet(pet: Pet | null) {
    currentPet.value = pet
  }

  return {
    pets,
    currentPet,
    fetchPets,
    createPet,
    updatePet,
    deletePet,
    setCurrentPet
  }
})
