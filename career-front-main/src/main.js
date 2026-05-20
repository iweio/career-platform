import { createApp } from 'vue'
import App from './App.vue'
import router from './router' // ✅ 引入 router
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

const app = createApp(App)

// 注册 Pinia
app.use(createPinia())

// ✅ 必须注册 router
app.use(router)

// 注册 Element Plus
app.use(ElementPlus)

// 全局注册图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.mount('#app')