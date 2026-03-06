import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api'
import type { CurrentUser } from '@/types'

export const useUserStore = defineStore('user', () => {
  const user = ref<CurrentUser | null>(null)
  const token = ref<string>('')

  const isLoggedIn = computed(() => !!token.value)
  const roles = computed(() => user.value?.roles || [])

  function setToken(newToken: string) {
    token.value = newToken
    localStorage.setItem('access_token', newToken)
  }

  function setUser(newUser: CurrentUser) {
    user.value = newUser
  }

  async function fetchCurrentUser() {
    try {
      const { data } = await authApi.getCurrentUser()
      user.value = data
      return data
    } catch (error) {
      logout()
      throw error
    }
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('access_token')
  }

  function initFromStorage() {
    const storedToken = localStorage.getItem('access_token')
    if (storedToken) {
      token.value = storedToken
    }
  }

  return {
    user,
    token,
    isLoggedIn,
    roles,
    setToken,
    setUser,
    fetchCurrentUser,
    logout,
    initFromStorage
  }
})
