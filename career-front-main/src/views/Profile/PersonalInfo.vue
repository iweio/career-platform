<template>
  <div class="personal-info-report">
    <el-row :gutter="20" class="row-first">
      <el-col :span="16">
        <el-card class="glass-card header-card">
          <div class="user-profile">
            <el-avatar :size="70" :src="avatarUrl" class="user-avatar" />
            <div class="user-text">
              <div class="name-row">
                <h2>{{ userInfo.name || '未设置姓名' }}</h2>
                <el-tag size="small" class="status-tag">分析已就绪</el-tag>
              </div>
              <p class="sub-info">
                <el-icon><School /></el-icon> {{ userInfo.school || '未提供学校信息' }}
                <el-divider direction="vertical" />
                <el-icon><Message /></el-icon> {{ userInfo.email || '未提供邮箱' }}
              </p>
            </div>
            <el-button class="re-edit-btn" @click="$emit('re-edit')">重新编辑经历</el-button>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="glass-card score-card">
          <div class="score-container">
            <span class="label">综合评分</span>
            <div class="big-score">{{ competitivenessScore }}</div>
            <el-tag size="small" class="score-tag">综合竞争力指数</el-tag>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="row-second">
      <el-col :span="8">
        <el-card class="glass-card detail-card">
          <template #header><div class="card-header">学习技能完整度</div></template>
          <div class="progress-box">
            <el-progress 
              type="circle" 
              :percentage="displayPercentage" 
              :width="140"
              :stroke-width="12"
              color="#70a1ff" 
            />
            <p class="chart-tip">简历信息覆盖率良好</p>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="glass-card detail-card">
          <template #header><div class="card-header">核心竞争力模型</div></template>
          <div v-show="!loading" ref="radarRef" class="chart-container"></div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="glass-card detail-card">
          <template #header><div class="card-header">技能词云</div></template>
          <div v-show="!loading" ref="wordCloudRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="row-third">
      <el-col :span="24">
        <el-card class="glass-card ai-report-card">
          <template #header>
            <div class="card-header">
              <el-icon><MagicStick /></el-icon> AI 深度诊断报告
            </div>
          </template>
<div class="report-content-grid">
  <div v-if="aiSuggestions" class="report-item">
    <p>{{ aiSuggestions }}</p>
  </div>
  <div v-else class="report-item empty-report">
    <el-icon><InfoFilled /></el-icon>
    <p>请先前往个人中心完成简历分析与岗位匹配，系统将自动生成 AI 深度诊断报告。</p>
  </div>
</div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, defineProps, defineEmits, nextTick } from 'vue'
import { School, Message, MagicStick, InfoFilled } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { profileApi } from '@/api/profile'

const props = defineProps(['userInfo'])
const emit = defineEmits(['re-edit'])

const loading = ref(true)
const radarRef = ref(null)
const wordCloudRef = ref(null)
const competitivenessScore = ref(88)
const aiSuggestions = ref('')
const radarValues = ref([85, 90, 95, 95, 80, 85, 60])
const wordCloudData = ref([
  { name: '数据结构与算法', value: 80 }, { name: 'Java', value: 60 },
  { name: '自主学习', value: 65 }, { name: '团队统筹', value: 70 },
  { name: '软件开发', value: 55 }, { name: '跨部门协作', value: 55 },
])

const loadAnalysis = async () => {
  try {
    const { data } = await profileApi.analysis()
    if (data.success && data.data) {
      const d = data.data
      if (d.competitiveness_score) competitivenessScore.value = d.competitiveness_score
      if (d.radar_data?.length) radarValues.value = d.radar_data
      if (d.word_cloud?.length) wordCloudData.value = d.word_cloud
      if (d.analysis_report?.summary) aiSuggestions.value = d.analysis_report.summary
    }
  } catch { /* keep mock fallback */ }
}

// 🌟 2. 声明图表实例变量（防止 ReferenceError）
let radarInstance = null
let wordCloudInstance = null

const avatarUrl = 'https://ui-avatars.com/api/?name=User&background=ebf5ff&color=70a1ff'

const handleResize = () => {
  radarInstance?.resize()
  wordCloudInstance?.resize()
}

onMounted(async () => {
  await loadAnalysis()
  await nextTick()
  loading.value = false
  setTimeout(() => {
    initRadarChart()
    initWordCloud()
    window.addEventListener('resize', handleResize)
  }, 150)
})

// 🌟 4. 这里的销毁和注销很重要
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  radarInstance?.dispose()
  wordCloudInstance?.dispose()
})

const displayPercentage = ref(0)
onMounted(() => {
  // 2. 延迟 800 毫秒（或者你喜欢的时间）再显示数值
  // 这样用户进入页面时会先看到进度条从 0 动画滑动到 85
  setTimeout(() => {
    displayPercentage.value = 85
  }, 800) 
})

const initRadarChart = () => {
  if (!radarRef.value) return
  if (radarInstance) radarInstance.dispose()
  
  // 修正：只初始化一次并赋值给变量
  radarInstance = echarts.init(radarRef.value)
  radarInstance.setOption({
    radar: {
      indicator: [
        { name: '专业技能', max: 100 },
        { name: '创新能力', max: 100 },
        { name: '学习能力', max: 100 },
        { name: '实习能力', max: 100 },
        { name: '抗压能力', max: 100 },
        { name: '沟通能力', max: 100 },
        { name: '证书', max: 100 },
      ],
      radius: '60%',
      axisName: { color: '#475569', fontWeight: 'bold', fontSize: 12 },
      axisLine: { lineStyle: { color: 'rgba(112, 161, 255, 0.5)' } },
      splitLine: { lineStyle: { color: 'rgba(112, 161, 255, 0.4)' } },
      splitArea: { areaStyle: { color: ['rgba(255, 255, 255, 0.05)', 'rgba(112, 161, 255, 0.1)'] } }
    },
    series: [{
      type: 'radar',
      data: [{
        value: radarValues.value,
        areaStyle: { color: 'rgba(112, 161, 255, 0.25)' },
        lineStyle: { color: '#70a1ff', width: 2.5 },
        itemStyle: { color: '#70a1ff' }
      }]
    }]
  })
}

const initWordCloud = () => {
  if (!wordCloudRef.value) return
  if (wordCloudInstance) wordCloudInstance.dispose()
  
  wordCloudInstance = echarts.init(wordCloudRef.value)
// 更加明亮、通透的浅色调
const colorPalette = ['#7dd3fc', '#a5b4fc', '#99f6e4', '#fef08a']
const data = wordCloudData.value
  
  wordCloudInstance.setOption({
    series: [{
      type: 'graph', 
      layout: 'force',
      roam: true, 
      draggable: true, 
      force: { repulsion: 60, edgeLength: 40 },
      data: data.map((i, index) => ({ 
        name: i.name, 
        symbolSize: i.value, 
        itemStyle: { 
          color: colorPalette[index % colorPalette.length],
          shadowBlur: 10,
          shadowColor: 'rgba(112, 161, 255, 0.2)' 
        } 
      })),
      label: { show: true, fontSize: 12, color: '#475569', fontWeight: 'bold' }
    }]
  })
}
</script>

<style scoped lang="scss">
.personal-info-report {
  display: flex; flex-direction: column; gap: 20px; padding: 10px;
}

.glass-card {
  background: rgba(255, 255, 255, 0.45) !important;
  backdrop-filter: blur(15px);
  border-radius: 20px;
  /* 🌟 边框改为淡蓝色 */
  border: 1px solid rgba(112, 161, 255, 0.15) !important;
  box-shadow: 0 8px 32px rgba(112, 161, 255, 0.05);
  height: 100%;
  transition: all 0.3s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.55) !important;
    border-color: rgba(112, 161, 255, 0.3) !important;
  }

  :deep(.el-card__header) {
    border-bottom: 1px solid rgba(112, 161, 255, 0.1) !important;
  }
}

.row-first {
  .user-profile {
    display: flex; align-items: center; gap: 24px; height: 100px;
    .user-text { 
      flex: 1; 
      h2 { margin: 0; color: #1e293b; } 
      .sub-info { color: #64748b; font-size: 14px; margin-top: 5px; } 
    }
    
    /* 🌟 Tag 颜色修改 */
    :deep(.status-tag) {
      background: rgba(112, 161, 255, 0.1) !important;
      color: #70a1ff !important;
      border: 1px solid rgba(112, 161, 255, 0.2) !important;
    }

    /* 🌟 按钮颜色修改 */
    .re-edit-btn {
      margin-left: auto; background: transparent; 
      border: 1px solid rgba(112, 161, 255, 0.3); color: #70a1ff;
      &:hover { background: rgba(112, 161, 255, 0.05); }
    }
  }

  .score-card {
    .score-container {
      display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100px;
      .label { font-size: 12px; color: #94a3b8; }
      /* 🌟 分数改用淡蓝渐变 */
      .big-score { 
        font-size: 48px; font-weight: 800; 
        background: linear-gradient(135deg, #0e3378 0%, #bdc3fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1; margin: 5px 0; 
      }
      :deep(.el-tag) { background: rgba(112, 161, 255, 0.05) !important; color: #70a1ff !important; border: none; }
    }
  }
}

/* 找到对应的词云容器样式 */
/* 请找到这部分样式，并加上注释了“🌟”的两行 */
.row-second {
  .detail-card {
    height: 320px;
    /* 1. 确保卡片本身不出现滚动条 */
    overflow: hidden !important; 

    /* 2. 🌟 关键：强制覆盖 Element Plus 卡片内部容器的溢出设置 */
    :deep(.el-card__body) {
      height: 270px; 
      width: 100%;
      display: flex;
      flex-direction: column;
      align-items: center;    
      justify-content: center; 
      padding: 0; 
      overflow: hidden !important; /* 🌟 加上这一行，干掉内层滚动条 */
    }

    .chart-container { 
      width: 100%; 
      height: 240px; 
      flex: 1;
      /* 3. 确保 ECharts 容器也不会因为微小溢出产生滚动 */
      overflow: hidden; 
    }
  }
}

.row-third {
  .ai-report-card {
    .card-header { 
      display: flex; align-items: center; gap: 8px; font-weight: bold; color: #70a1ff; 
    }
    .report-content-grid {
      display: grid; grid-template-columns: repeat(3, 1fr); gap: 30px; padding: 10px 0;
      .report-item {
  margin-bottom: 30px;

  h4 {
    font-size: 17px;
    font-weight: 700;
    color: #1e1b4b;
    margin-bottom: 16px;
    display: flex;
    align-items: center;

    // 增加一个小装饰条
    &::before {
      content: "";
      width: 4px;
      height: 18px;
      background: #6366f1;
      margin-right: 10px;
      border-radius: 2px;
    }
  }

  p {
    font-size: 14px;
    line-height: 1.8;
    color: #475569;
    margin-bottom: 12px; // 段落之间的间距
    text-align: justify; // 保证边缘整齐
    
    // 如果不想要缩进，可以删掉下面这行
    text-indent: 0;
  }

  &.empty-report {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    grid-column: 1 / -1;
    padding: 40px 20px;
    color: #94a3b8;
    font-size: 14px;
    .el-icon { font-size: 40px; margin-bottom: 12px; color: #cbd5e1; }
  }
}
    }
  }
}
</style>