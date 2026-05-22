import api from './client'

export const profileApi = {
  analysis() {
    return api.get('/profile/analysis')
  },
}
