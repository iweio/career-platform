import api from './client'

export const learningPlanApi = {
  polish(data) {
    return api.post('/learning-plan/polish', data)
  },
  exportPlan(data) {
    return api.post('/learning-plan/export', data)
  },
  getTasks() {
    return api.get('/learning-plan/tasks')
  },
}
