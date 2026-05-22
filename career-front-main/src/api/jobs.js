import api from './client'

export const jobsApi = {
  list(params = {}) {
    return api.get('/jobs', { params })
  },
  detail(id) {
    return api.get(`/jobs/${id}`)
  },
  categories() {
    return api.get('/jobs/categories')
  },
  hotTags() {
    return api.get('/jobs/hot-tags')
  },
  graph(id) {
    return api.get(`/jobs/${id}/graph`)
  },
  promotion(id) {
    return api.get(`/jobs/${id}/promotion`)
  },
}
