import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useDescriptionStore = defineStore('description', () => {
  const description = ref("");
  return { description }
})
