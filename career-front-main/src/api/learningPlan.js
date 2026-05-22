import api from './client'

export const learningPlanApi = {
  generate(data) {
    return api.post('/learning-plan/generate', data, { timeout: 120000 })
  },
  polish(data) {
    return api.post('/learning-plan/polish', data)
  },
  dailyTasks(data) {
    return api.post('/learning-plan/daily-tasks', data)
  },
  adjust(data) {
    return api.post('/learning-plan/adjust', data)
  },
  exportPlan(data) {
    return api.post('/learning-plan/export', data)
  },
  getTasks() {
    return api.get('/learning-plan/tasks')
  },
  updateTask(taskId, status) {
    return api.put(`/learning-plan/tasks/${taskId}`, { status })
  },
  completeTask(taskId) {
    return api.post(`/learning-plan/tasks/${taskId}/complete`)
  },
}
