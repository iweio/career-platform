<template>
  <div class="personal-info-report">
    <el-row :gutter="20" class="row-first">
      <el-col :span="16">
        <el-card class="glass-card header-card">
          <div class="user-profile">
            <el-avatar :size="70" :src="avatarUrl" class="user-avatar" />
            <div class="user-text">
              <div class="name-row">
                <h2>{{ userInfo.name || '张三' }}</h2>
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
            <el-tag size="small" class="score-tag">超越 92% 同类人才</el-tag>
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
  <div class="report-item">
    <h4>核心优势</h4>
    <p>&nbsp;&nbsp;&nbsp;&nbsp;您的职业基因呈现出极强的「高起点与快转化」特征。其核心竞争力在于卓越的知识内化效率与大厂级工程规范的深度融合。在学习能力与实习能力维度上，您均获得了九十五分的顶尖评价，这直接反映在您三点七的高绩点和专业前百分之十的学术排名中。</p>
    
    <p>&nbsp;&nbsp;&nbsp;&nbsp;更核心的表现是，您在面对高难度、高密度的知识体系时，拥有极强的底层逻辑拆解能力。这种素质在您的腾讯实习经历中得到了完美转化，您不仅完成了业务功能的开发，更深度参与了从需求初步拆解到最终测试上线的全生命周期闭环。</p>
    
    <p>&nbsp;&nbsp;&nbsp;&nbsp;这意味着您已初步建立起大型分布式系统的工程思维，能够无缝对接一线互联网平台的开发节奏与技术标准。这种「学术深厚」与「实战扎实」并存的双重背景，构成了您在同龄应届生中极具杀伤力的职业竞争壁垒，让您在技术理解力与执行稳健性上都具备了显著优势。</p>
  </div>

  <div class="report-item">
    <h4>提分建议</h4>
    <p>&nbsp;&nbsp;&nbsp;&nbsp;针对您目前证书竞争力评分与其技术深度严重脱节的现状，建议实施精准的「专业背书升级」战略。目前的证书短板可能在大型企业或外企的初筛环节成为潜在的阻碍因素，因此应当采取「降维打击」策略，将您的实战经验转化为行业公认的官方证明。</p>
    
    <p>&nbsp;&nbsp;&nbsp;&nbsp;鉴于您在大创项目中展现出的知识图谱与算法背景，下一步应从「功能实现者」向「架构设计者」跨越。建议优先考取与后端开发、云架构高度相关的专业级认证，如阿里云 ACP 或 AWS 解决方案架构师。这能迅速将您的技术敏感度转化为行业认可的专业权威。</p>
    
    <p>&nbsp;&nbsp;&nbsp;&nbsp;此外，通过获取这些高含金量的证书，可以有效消除纸面证明与实际工程实力之间的非对称性。这不仅能为后续向技术统筹或项目管理转型提供必要的准入背书，更能让您的简历在算法筛选阶段脱颖而出，彻底补齐职业竞争力拼图的最后一块缺失环节。</p>
  </div>

  <div class="report-item">
    <h4>职业展望</h4>
    <p>&nbsp;&nbsp;&nbsp;&nbsp;基于您在 Java 与 Python 双栖开发的深厚背景，您的职业进化路径清晰地指向了具备技术领导力潜质的「准专家级」开发者。在短期内，您的目标应精准锁定头部互联网平台的高级后端开发或算法工程化岗位，主导核心业务的高并发模块设计，建立深厚的技术信用。</p>
    
    <p>&nbsp;&nbsp;&nbsp;&nbsp;从长远战略视角来看，凭借您在沟通维度展现出的跨部门协作能力与团队统筹潜质，您的职业天花板将延伸至技术架构师或研发部门负责人。您对前沿技术趋势的预判力将帮助您在职场黄金期主导中大型技术团队的战略规划与选型决策，实现从技术执行向技术决策的跃迁。</p>
    
    <p>&nbsp;&nbsp;&nbsp;&nbsp;您不仅有望成为某一技术领域的深度专家，更能成长为平衡业务逻辑与技术演进的复合型技术领袖。在未来三到五年内，通过在工业界一线快速沉淀深厚的技术资产，您将建立起不可替代的个人品牌影响力，在瞬息万变的技术生态中始终占据核心的职业竞争位点。</p>
  </div>
</div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, defineProps, defineEmits, nextTick } from 'vue'
import { School, Message, MagicStick } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

const props = defineProps(['userInfo'])
const emit = defineEmits(['re-edit'])

// 🌟 1. 补全缺失的响应式变量声明
const loading = ref(true) 
const radarRef = ref(null)
const wordCloudRef = ref(null)
const competitivenessScore = ref(88)
const aiSuggestions = ref('')

// 🌟 2. 声明图表实例变量（防止 ReferenceError）
let radarInstance = null
let wordCloudInstance = null

const avatarUrl = 'https://ui-avatars.com/api/?name=User&background=ebf5ff&color=70a1ff'

// 模拟获取数据
const mockFetchData = () => {
  return new Promise((resolve) => {
    setTimeout(() => {
      competitivenessScore.value = 87.5
      aiSuggestions.value = "根据您的经历分析，您在技术架构方面表现卓越..." 
      loading.value = false // 现在 loading 已定义，不会报错了
      resolve()
    }, 800)
  })
}

// 🌟 3. 补全缺失的适配函数
const handleResize = () => {
  radarInstance?.resize()
  wordCloudInstance?.resize()
}

onMounted(async () => {
  await mockFetchData()
  await nextTick()
  
  // 延迟执行以确保容器宽高已由浏览器计算完毕
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
        value: [85, 90, 95, 95, 80, 85, 60],
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
const colorPalette = ['#7dd3fc', '#a5b4fc', '#99f6e4', '#fef08a']; const data = [
    { name: '数据结构与算法', value: 80 }, { name: 'Java', value: 60 }, 
    { name: '自主学习', value: 65 }, { name: '团队统筹', value: 70 },
    { name: '软件开发', value: 55 }, { name: '跨部门协作', value: 55 }
  ]
  
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
}
    }
  }
}
</style>