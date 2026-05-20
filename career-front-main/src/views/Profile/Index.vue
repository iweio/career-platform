<template>
  <div class="personal-center">
    <aside class="sidebar">
      <div class="avatar-placeholder">
        <el-avatar :size="80" :src="avatarUrl" />
      </div>
     <el-menu :default-active="activeTab" class="menu" @select="handleMenuSelect">
      <el-menu-item index="info">
        <el-icon><User /></el-icon>
        <span>个人信息</span>
      </el-menu-item>
      <el-menu-item index="report">
        <el-icon><DataAnalysis /></el-icon>
        <span>AI 职业分析</span>
      </el-menu-item>
      <el-menu-item index="growth">
        <el-icon><TrendCharts /></el-icon>
        <span>成长追踪中心</span>
      </el-menu-item>
      <el-menu-item index="report-export">
        <el-icon><DocumentCopy /></el-icon>
        <span>报告优化与导出</span>
      </el-menu-item>
      <el-menu-item index="favorite" class="menu-item-bottom">
      <el-icon><Star /></el-icon>
      <span>目标岗位</span>
    </el-menu-item>
    </el-menu>
    </aside>

    <main class="main-content">
      <div class="content-wrapper">
        
        <template v-if="activeTab === 'info'">
          <div v-if="!isInfoFilled" class="ai-chat-layout">
            <div class="chat-dashboard-upper">
              <section class="chat-section">
                <div class="chat-header">
                  <div class="header-left">
                    <div class="status-indicator">
                      <span class="pulse-dot"></span>
                    </div>
                    <div class="header-text">
                      <h3 class="chat-title">职能助手</h3>
                    </div>
                  </div>
                    <div class="header-right">
                      <el-tooltip effect="dark" content="已開啟最高精準度解析" placement="top">
                        <el-tag size="small" class="ai-mode-tag">
                          智能模式
                        </el-tag>
                      </el-tooltip>
                    </div>
                </div>

                <div ref="messageListRef" class="message-list">
                  <div v-for="msg in chatMessages" :key="msg.id" :class="['message-item', msg.role]">
                    <div class="message-avatar">
                      <div v-if="msg.role === 'assistant'" class="ai-icon">
                        <el-icon><MagicStick /></el-icon>
                      </div>
                      <el-avatar v-else :size="36" src="https://ui-avatars.com/api/?name=User&background=667eea&color=fff" />
                    </div>
                    
                    <div class="message-content-wrapper">
                      <div class="message-bubble">
                        {{ msg.content }}
                      </div>
                      <span class="message-time">刚刚</span>
                    </div>
                  </div>

                  <div v-if="loading" class="message-item assistant">
                    <div class="message-avatar">
                      <div class="ai-icon spinning">
                        <el-icon><Loading /></el-icon>
                      </div>
                    </div>
                    <div class="message-content-wrapper">
                      <div class="message-bubble loading-dots">
                        <span></span><span></span><span></span>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="chat-input-area">
                  <div class="input-container">
                    <el-input
                      v-model="inputValue"
                      type="textarea"
                      :rows="2"
                      placeholder="在此粘贴简历内容..."
                      resize="none"
                      @keydown.enter.prevent="handleSend"
                    />
                    <div class="input-footer">
                      <el-upload 
                        action="#" 
                        :auto-upload="false" 
                        :show-file-list="false"
                        :on-change="handleFileChange"
                        accept=".pdf,.doc,.docx,.txt"
                      >
                        <el-button link icon="Upload">
                          {{ attachedFile ? '更换附件' : '上传附件' }}
                        </el-button>
                      </el-upload>
                      
                      <div v-if="attachedFile" class="file-tag">
                        <el-tag closable size="small" @close="removeFile">
                          {{ attachedFile.name }}
                        </el-tag>
                      </div>

                      <el-button 
                        type="primary" 
                        circle 
                        icon="Promotion" 
                        @click="handleSend" 
                        class="send-btn"
                      />
                    </div>
                  </div>
                </div>
              </section>

              <section class="dashboard-preview-section">
                <div class="artifact-card">
                  <div class="artifact-header">
                    <h4>实时画像预览</h4>
                    <div class="completion-status">
                      <span class="percentage">
                        {{ currentStepIndex === 0 ? '0%' : currentStepIndex === 1 ? '14%' : currentStepIndex === 2 ? '100%' : '100%' }}
                      </span>
                      <span class="label">维度完善度</span>
                    </div>
                  </div>
                  
                  <div class="scroll-container">
                    <div v-if="currentStepIndex > 0" class="highlight-tags">
                      <el-tag v-for="tag in currentHighlights" :key="tag" size="small" effect="plain" class="glow-tag">
                        {{ tag }}
                      </el-tag>
                    </div>

                    <div class="preview-radar-placeholder">
                      <RadarChart :data="currentRadarData" />
                    </div>

                    <div v-if="currentStepIndex > 0" class="dimension-grid">
                      <div 
                        v-for="(val, key) in dimensionDetails" 
                        :key="key" 
                        :class="['dimension-card', val.type]"
                      >
                        <div class="dim-header">
                          <span class="dim-name">{{ key }}</span>
                          <span :class="['dim-status', val.type]">
                            {{ val.type === 'success' ? '✓' : '○' }} {{ val.status }}
                          </span>
                        </div>
                        <p class="dim-desc">{{ val.desc }}</p>
                      </div>
                    </div>
                    
                    <p class="empty-preview-tip">
                    </p>
                  </div>
                </div>
              </section>
            </div>

            <div class="bottom-action-bar">
              <el-button 
                type="primary" 
                class="analyze-btn" 
                size="large"
                @click="saveAndContinue"
                :loading="loading"
              >
                <el-icon class="el-icon--left"><MagicStick /></el-icon>
                保存并开始 AI 深度分析
              </el-button>
            </div>
          </div>
          <div v-else class="dashboard-result-view">
             <PersonalInfo :user-info="userInfo" @re-edit="isInfoFilled = false" />
          </div>
        </template>

        <div v-else-if="activeTab === 'report'" class="sub-page">
          <AIReport />
        </div>
        <div v-else-if="activeTab === 'growth'" class="sub-page">
          <GrowthTracker />
        </div>
        <div v-else-if="activeTab === 'report-export'" class="sub-page">
          <PolishAndExport />
        </div>
        <div v-else-if="activeTab === 'favorite'" class="sub-page">
          <FavoriteJobs />
        </div>
        
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, nextTick, computed } from 'vue'
import { Refresh, Histogram, Upload } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// 导入你的子组件
import PersonalInfo from './PersonalInfo.vue'
import AIReport from './AIReport.vue'
import GrowthTracker from './GrowthTracker.vue'
import PolishAndExport from './PolishAndExport.vue'
import FavoriteJobs from './FavoriteJobs.vue'
import RadarChart from '../../components/RadarChart.vue'
const attachedFile = ref(null) // 存储文件对象

// 🌟 处理文件选择逻辑
const handleFileChange = (file) => {
  // 校验文件大小 (例如 5MB 限制)
  const isLt5M = file.size / 1024 / 1024 < 5
  if (!isLt5M) {
    ElMessage.error('上传附件大小不能超过 5MB!')
    return
  }
  
  attachedFile.value = file.raw // 存储原始 File 对象
  ElMessage.success(`已添加附件: ${file.name}`)
}

// 🌟 移除附件逻辑
const removeFile = () => {
  attachedFile.value = null
}

const activeTab = ref('info')
const isInfoFilled = ref(false)
const loading = ref(false)
const inputValue = ref('')
const messageListRef = ref(null)
const avatarUrl = ref('https://ui-avatars.com/api/?name=User&size=120&background=409EFF&color=fff')

const userInfo = ref({ name: '', email: '', rawResumeText: '', school: '' })

// --- 新增：模拟 AI 剧本配置 ---
const scriptSteps = [
  {
    answer: "你提到参加过创新创业大赛，可以具体聊聊你的项目是什么，以及取得了什么样的成绩吗？ 关于在腾讯的实习经历，你当时是在哪个岗位实习呢？主要负责哪些工作，有没有什么让你印象深刻的成果呀？ 除了Python编程，你有没有考取过什么相关的证书呢？ 你觉得自己的学习能力怎么样呀？有没有什么快速掌握新知识的例子可以分享呢？ 在团队合作或者项目中，你通常是如何与队友沟通的呢？ 面对压力比较大的任务或项目时，你一般会怎么应对呢？",
    radarData: [40, 30, 0, 50, 0, 0, 0], // 对应 9 维能力的数值
  },
  {
    answer: "🎉 信息已完善！恭喜您完成了所有7个维度的信息采集",
    radarData: [85, 90, 95, 95, 80, 85, 60],
  },
  {
    answer: "分析已全部完成！基于你目前的表现，我为你匹配了‘前端开发’、‘UI 交互’等目标岗位。你可以点击下方的‘保存并开始 AI 深度分析’，查看完整的职业路线图和优化策略。",
    radarData: [90, 85, 90, 80, 85, 90, 85],
  }
];



// --- 新增：状态追踪变量 ---
const currentStepIndex = ref(0); // 记录当前对话到第几轮了
const currentRadarData = ref([0, 0, 0, 0, 0, 0, 0]); // 传给右侧看板的数据

// 在 script 标签内添加
const currentHighlights = computed(() => {
  const highlights = [
    [], // 初始状态
    ['熟悉 Python'],
    ['计算机二级', '掌握数据结构与算法', '精通Java/Python等开发技术']
  ];
  return highlights[currentStepIndex.value] || highlights[2];
});

const currentSuggestion = computed(() => {
  const suggestions = [
    '',
    '建议强化实战项目中的困难解决方案描述。',
    '画像已成熟，建议考取计算机二级证书并加强抗压练习。'
  ];
  return suggestions[currentStepIndex.value] || suggestions[2];
});

const chatMessages = ref([
  { id: 1, role: 'assistant', content: '您好！我是您的AI职业向导。您可以直接粘贴简历内容或上传文件。' }
])

const quickActions = [
  { label: '📝 开始分析', command: '分析我的简历' },
  { label: '🔍 检查完整度', command: '简历完整度检查' }
]

const progressValue = computed(() => userInfo.value.rawResumeText.length > 50 ? 85 : 10)

// 🌟 修复核心：确保菜单选择逻辑能干净地切换 activeTab
const handleMenuSelect = (index) => {
  activeTab.value = index
}

// 🌟 修改发送逻辑
const handleSend = async () => {
  // 1. 拦截逻辑：文字和附件都为空时才拦截
  if (!inputValue.value.trim() && !attachedFile.value) {
    ElMessage.warning('请输入内容或上传简历附件')
    return
  }

  // 2. 构造用户消息内容
  // 如果有文件，展示 [附件:文件名]；如果有文字，也一并拼接到内容里
  let displayContent = inputValue.value;
  if (attachedFile.value) {
    displayContent += displayContent ? `\n[附件: ${attachedFile.value.name}]` : `[附件: ${attachedFile.value.name}]`;
  }

  // 3. 🌟 关键：推送到聊天记录数组 (注意：这里使用你原本代码中的 chatMessages)
  chatMessages.value.push({
    id: Date.now(),
    role: 'user',
    content: displayContent,
    time: new Date().toLocaleTimeString()
  });

  // 4. 更新简历文本（模拟你的业务逻辑）
  if (inputValue.value) {
    userInfo.value.rawResumeText += inputValue.value;
  }

  // 5. 清空输入状态
  const savedInputValue = inputValue.value; // 如果后续 API 需要用到，可以先存一下
  inputValue.value = '';
  attachedFile.value = null; // 清空附件，让 UI 上的标签消失

  // 6. UI 反馈与滚动
  loading.value = true;
  await scrollToBottom();

  // 7. 模拟 AI 回复
  // 🌟 找到原有 handleSend 的 setTimeout 部分并替换
setTimeout(async () => {
  // 1. 根据当前步数获取剧本内容，如果超出剧本长度则循环最后一条
  const step = scriptSteps[currentStepIndex.value] || scriptSteps[scriptSteps.length - 1];

  // 2. 将硬编码的回答推送到聊天列表
  chatMessages.value.push({
    id: Date.now(),
    role: 'assistant',
    content: step.answer, // 使用剧本里的回答
    time: new Date().toLocaleTimeString()
  });

  // 3. 🌟 关键：更新右侧看板所需的数据变量
  currentRadarData.value = step.radarData;

  // 4. 对话步数加 1
  currentStepIndex.value++;

  loading.value = false;
  await scrollToBottom();
}, 3000); // 稍微延长到 1.2s，模拟 AI 思考和更新画像的过程
}

const saveAndContinue = () => {
  isInfoFilled.value = true
  ElMessage.success('简历保存成功！')
  sessionStorage.setItem('is_profile_completed', 'true');
}

const handleFileUpload = () => {
  ElMessage.success('文件解析中...')
}

const handleQuickAction = (cmd) => {
  inputValue.value = cmd
  handleSend()
}

const scrollToBottom = async () => {
  await nextTick()
  if (messageListRef.value) messageListRef.value.scrollTop = messageListRef.value.scrollHeight
}

const handleDeepAnalysis = () => {
  // 1. 设置临时标记，告知首页信息已填
  sessionStorage.setItem('is_profile_completed', 'true');
  
  // 2. 原有的跳转逻辑
  router.push('/').then(() => {
    // 强制刷新一下首页的状态（可选，如果 Home 逻辑没跑）
    window.location.reload(); 
  });
};

// 找到 Index.vue 中的 dimensionDetails 部分，替换为以下代码
const dimensionDetails = computed(() => {
  // 默认初始状态或第一轮对话的状态
  const defaultDetails = {
    "专业技能": { status: "已完善", desc: "会Python编程", type: "success" },
    "证书": { status: "未提及", desc: "用户未提及此维度", type: "info" },
    "创新能力": { status: "不清楚", desc: "用户提及但无具体例子", type: "warning" },
    "学习能力": { status: "未提及", desc: "用户未提及此维度", type: "info" },
    "抗压能力": { status: "未提及", desc: "用户未提及此维度", type: "info" },
    "沟通能力": { status: "未提及", desc: "用户未提及此维度", type: "info" },
    "实习能力": { status: "不清楚", desc: "用户提及但无具体例子", type: "warning" }
  };

  // 第二轮对话及以后（currentStepIndex >= 2）返回你要求的完整信息
  const completedDetails = {
    "专业技能": { 
      status: "已完善", 
      desc: "精通Java/Python等开发技术；扎实掌握数据结构与算法", 
      type: "success" 
    },
    "证书": { 
      status: "已完善", 
      desc: "持有计算机二级等专业证书", 
      type: "success" 
    },
    "创新能力": { 
      status: "已完善", 
      desc: "主导大创项目，运用知识图谱等技术实现创新方案，成果显著；参加过创新创业大赛", 
      type: "success" 
    },
    "学习能力": { 
      status: "已完善", 
      desc: "GPA 3.7/4.0，专业排名前10%；自主学习能力强，能快速掌握新技术", 
      type: "success" 
    },
    "抗压能力": { 
      status: "已完善", 
      desc: "能高效应对项目攻坚、多任务并行等高压场景，按时高质量完成目标", 
      type: "success" 
    },
    "沟通能力": { 
      status: "已完善", 
      desc: "具备优秀跨部门协作与团队统筹能力，高效推进项目落地", 
      type: "success" 
    },
    "实习能力": { 
      status: "已完善", 
      desc: "在腾讯实习过，参与企业软件开发全流程，完成功能开发、测试优化，积累扎实工程实践经验", 
      type: "success" 
    }
  };

  // 根据当前对话步数切换显示内容
  // 因为你在 handleSend 中每次回复后会 currentStepIndex.value++
  // 初始是 0，第一次回复后是 1，第二次回复后是 2
  return currentStepIndex.value >= 2 ? completedDetails : defaultDetails;
});
</script>

<style scoped lang="scss">
.personal-center {
  display: flex;
  min-height: 100vh;
}

/* 侧边栏整体重构 */
.sidebar {
  width: 260px;
  height: 93vh;
  background: rgba(255, 255, 255, 0.4); /* 半透明背景 */
  backdrop-filter: blur(20px); /* 毛玻璃效果 */
  border-right: 1px solid rgba(255, 255, 255, 0.5);
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
  z-index: 100;

  .avatar-placeholder {
    padding: 50px 0 30px;
    text-align: center;
    
    .el-avatar {
      box-shadow: 0 8px 16px rgba(118, 75, 162, 0.2);
      border: 2px solid #fff;
      transition: transform 0.3s ease;
      &:hover {
        transform: scale(1.05);
      }
    }
  }

  /* 菜单样式定制 */
  /* 菜单样式定制 */
  .el-menu {
    border: none;
    background: transparent;
    padding: 0 16px 20px;
    
    /* 🌟 必须：开启 flex 布局 */
    display: flex;
    flex-direction: column;
    height: calc(100% - 160px); /* 减去上方头像占用的空间 */

    .el-menu-item {
      height: 54px;
      line-height: 54px;
      margin-bottom: 8px;
      border-radius: 12px;
      color: #64748b;
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

      span {
        font-weight: 500;
        margin-left: 8px;
      }

      /* 鼠标悬停 */
      &:hover {
        background: rgba(186, 211, 246, 0.318) !important;
        color: #68788c;
        transform: translateX(4px);
      }

      /* 激活状态 */
      &.is-active {
        background: linear-gradient(135deg, #bbd7f6a3 0%, #ffffffb6 100%) !important;
        color: #221b4f !important;
        box-shadow: 0 4px 12px rgba(75, 98, 162, 0.3);
      }

&.menu-item-bottom {
  margin-top: auto !important;
  margin-bottom: 20px;
  
  /* 🌟 1. 强制去掉任何背景色和边框，保持透明 */
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  backdrop-filter: none !important;

  /* 文字和图标默认状态 */
  span {
    font-size: 14px;
    color: #64748b;
    transition: all 0.3s ease; /* 确保字号变化平滑 */
  }
  
  :deep(.el-icon) {
    font-size: 18px;
    color: #64748b;
    transition: all 0.3s ease;
  }

  /* 🌟 2. 鼠标悬停：只改颜色和字号 */
  &:hover {
    background: transparent !important; /* 再次确保没有背景 */
    transform: none !important;        /* 去掉之前的位移动画 */
    
    span {
      color: #4f46e5 !important;       /* 变成深紫色 */
      font-size: 16px !important;      /* 字号变大 */
      font-weight: 600 !important;
    }
    
    :deep(.el-icon) {
      color: #4f46e5 !important;       /* 图标同步变色 */
      font-size: 20px !important;      /* 图标同步变大 */
    }
  }

  /* 🌟 3. 点击选中（激活状态）：只改颜色和字号 */
  &.is-active {
    background: transparent !important; /* 强制透明 */
    box-shadow: none !important;
    
    span {
      color: #1e1b4b !important;       /* 选中的文字颜色更深 */
      font-size: 16px !important;      /* 保持变大的状态 */
      font-weight: 700 !important;
    }
    
    :deep(.el-icon) {
      color: #1e1b4b !important;
      font-size: 20px !important;
    }
  }
}
    }
  }
}

/* 找到 .chat-section 下的 .chat-header 样式进行替换 */
.chat-header {
  padding: 16px 24px; /* 增加内边距更显轻盈 */
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.03); /* 极细的分割线 */
  transition: all 0.3s ease;

  .header-left {
    display: flex;
    align-items: center;
    gap: 12px;

    /* 🌟 AI 状态指示器样式 */
    .status-indicator {
      width: 14px;
      height: 14px;
      display: flex;
      align-items: center;
      justify-content: center;

      .pulse-dot {
        width: 8px;
        height: 8px;
        background-color: #67c23a; /* ElementPlus 成功绿色 */
        border-radius: 50%;
        position: relative;
        box-shadow: 0 0 6px #67c23a;

        /* 呼吸灯动画效果 */
        &::after {
          content: "";
          width: 100%;
          height: 100%;
          background-color: #67c23a;
          border-radius: 50%;
          position: absolute;
          left: 0;
          top: 0;
          animation: pulse 2s infinite ease-in-out;
          opacity: 0.8;
        }
      }
    }

    .header-text {
      display: flex;
      flex-direction: column;

      .chat-title {
        margin: 0;
        font-size: 16px;
        font-weight: 600;
        color: #1e293b; /* 更高级的灰黑色 */
        line-height: 1.2;
      }

      .ai-status-desc {
        font-size: 11px;
        color: #94a3b8; /* 较浅的灰色 */
        margin-top: 2px;
      }
    }
  }

  .header-right {
    /* 🌟 智能模式 Tag 样式轻量化 */
/* 在 .chat-header 的样式中找到 .ai-mode-tag 并修改 */
    .ai-mode-tag {
      /* 减小内边距：上下 0，左右 12px（原先可能是默认值） */
      padding: 0 12px; 
      height: 28px;        /* 固定高度让它看起来更精致 */
      line-height: 26px;   /* 垂直居中 */
      border-radius: 14px; /* 圆角设置为高度的一半，形成完美的胶囊形状 */
      
      display: inline-flex;
      align-items: center;
      gap: 4px;            /* 图标和文字之间的间距 */
      
      /* 针对图片中显示的紫色样式优化 */
      background: rgba(28, 61, 111, 0.08) !important;
      color: #161e5d !important;
      border: 1px solid rgba(118, 75, 162, 0.2) !important;
      font-size: 13px;     /* 稍微调小字号更显高级 */
    }
  }
}

/* 呼吸灯动画 */
@keyframes pulse {
  0% { transform: scale(1); opacity: 0.8; }
  70% { transform: scale(2.5); opacity: 0; }
  100% { transform: scale(1); opacity: 0; }
}

/* 增强主内容区的呼吸感 */
.main-content {
  flex: 1;
  padding: 24px;
  background-color: #f1f5f9 !important;
  background-image: 
    /* 荧光紫 */
    radial-gradient(at 100% 100%, rgba(242, 181, 120, 0.271) 0px, transparent 40%),
    /* 顶部中心的一抹亮白 */
    radial-gradient(at 10% 0%, rgba(252, 252, 231, 0.8) 0px, transparent 30%) !important;
  overflow-y: auto;
}


/* 1. 整体布局容器 */
/* 1. 调整外层，确保它占据整个屏幕高度，并去掉可能存在的干扰 */
.ai-chat-layout {
  display: flex;
  flex-direction: column;
  /* 调小画布并居中 */
  width: 95%; 
  margin: 0 auto;
  /* 锁定高度，确保不超出屏幕产生滚动 */
  height: 90vh; 
  gap: 20px;
  overflow: hidden;
}

/* 2. 第一行：强制子元素高度同步 */
.chat-dashboard-upper {
  display: flex;
  gap: 24px;
  flex: 1;             /* 占据除按钮外的剩余高度 */
  min-height: 0;       /* 必须设置，否则 flex 内部滚动失效 */
  align-items: stretch; /* 强制左右两个 section 高度拉伸至一致 */
}

/* 3. 左侧对话框：内部结构调整 */
.chat-section {
  flex: 1.2;
  display: flex;
  flex-direction: column; /* 纵向排版，让 message-list 能撑开 */
  background: rgba(243, 247, 250, 0.233);
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0,0,0,0.05);
  border: 2px solid rgba(22, 40, 90, 0.034) !important;


  .message-list {
    flex: 1;           /* 核心：占据中间所有剩余空间 */
    overflow-y: auto;   /* 只有这里产生滚动 */
    padding: 20px;
  }
}

/* 4. 右侧看板：这是你之前失败的关键点 */
.dashboard-preview-section {
  flex: 0.8;
  display: flex;       /* 新增：开启 flex 模式 */
  flex-direction: column; /* 新增 */
  border-radius: 20px;
  border: 2px solid rgba(22, 40, 90, 0.034) !important;

  .artifact-card {
    flex: 1;           /* 核心修改：强制卡片填满整个 section 的高度 */
    display: flex;
    flex-direction: column;
    background: rgba(255, 255, 255, 0.4);
    backdrop-filter: blur(20px);
    border-radius: 28px;
    padding: 24px;
    border: 1px solid rgba(255, 255, 255, 0.7);

    /* 让内部的雷达图占位符也撑开 */
    .preview-radar-placeholder {
      flex: 1;         /* 让虚线框区域自动垂直拉伸 */
      display: flex;
      align-items: center;
      justify-content: center;
      background: rgba(255, 255, 255, 0.3);
      border-radius: 20px;
      border: 2px dashed rgba(0, 0, 0, 0.05);
      margin: 20px 0;
    }
  }
}

/* 5. 底部按钮区域 */
.bottom-action-bar {
  flex-shrink: 0;      /* 防止按钮被压缩 */
  display: flex;
  justify-content: center;
  padding: 10px 0;
  /* 在 SCSS 中找到或添加 .analyze-btn 的样式 */
.analyze-btn {
  /* 🌟 使用菜单同款渐变色 */
  background: linear-gradient(135deg, #fdfdfc 0%, #ebf2f6bb 100%) !important;
  border: none !important;
  color: rgb(23, 59, 105) !important;
  
  /* 增加阴影使其更有悬浮感 */
  box-shadow: 0 4px 15px rgba(75, 104, 162, 0.3);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
  
  /* 调整按钮形状与整体圆角风格一致 */
  border-radius: 12px;
  padding: 12px 28px !important;
  font-weight: 600;

  &:hover {
    /* 悬浮时轻微放大并加强阴影 */
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(75, 100, 162, 0.4);
    opacity: 0.9;
  }

  &:active {
    transform: translateY(0);
  }
}
}

/* 消息列表气泡样式优化 */
/* 消息列表基础布局 */
.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 30px; /* 增加内边距更显高级 */
  display: flex;
  flex-direction: column;
  gap: 24px;

  /* 自定义滚动条样式，更细更轻盈 */
  &::-webkit-scrollbar { width: 4px; }
  &::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.05); border-radius: 10px; }

  .message-item {
    display: flex;
    gap: 12px;
    max-width: 85%;
    align-items: flex-end; /* 头像与气泡底部对齐 */

    /* AI 助手样式 */
    &.assistant {
      align-self: flex-start;
      .ai-icon {
        width: 36px;
        height: 36px;
        background: linear-gradient(135deg, #989fed 0%, #153674c7 100%);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 18px;
        box-shadow: 0 4px 12px rgba(118, 75, 162, 0.2);
      }
      .message-bubble {
        background: #fff;
        color: #334155;
        border-radius: 16px 16px 16px 4px; /* 非对称圆角 */
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
      }
    }

    /* 用户样式 */
    &.user {
      flex-direction: row-reverse; /* 头像在右侧 */
      align-self: flex-end;
      .message-bubble {
        /* 采用更有层次的紫色渐变 */
        background: linear-gradient(135deg, #57a6ec 0%, #5779e999 100%);
        color: white;
        border-radius: 16px 16px 4px 16px;
        box-shadow: 0 8px 20px rgba(118, 75, 162, 0.15);
      }
      .message-time { text-align: right; }
    }
  }

  .message-content-wrapper {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .message-bubble {
    padding: 12px 18px;
    font-size: 14.5px;
    line-height: 1.6;
    word-break: break-word;
    position: relative;
    transition: all 0.3s ease;
    
    &:hover {
      transform: translateY(-1px);
    }
  }

  .message-time {
    font-size: 11px;
    color: #94a3b8;
    padding: 0 4px;
  }
}

/* 消息输入区域轻量化 */
.chat-input-area {
  padding: 24px;
  background: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(10px);
  border-top: 1px solid rgba(0, 0, 0, 0.03);

  .input-container {
    background: white;
    padding: 12px;
    border-radius: 16px;
    border: 1px solid rgba(0, 0, 0, 0.05);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.03);
    transition: all 0.3s ease;

    &:focus-within {
      border-color: #667eea;
      box-shadow: 0 10px 30px rgba(102, 126, 234, 0.1);
    }

    :deep(.el-textarea__inner) {
      border: none;
      box-shadow: none;
      font-size: 14px;
      color: #1e293b;
      &::placeholder { color: #cbd5e1; }
    }
  }
}

.input-footer {
  display: flex;
  justify-content: space-between; /* 关键：这会让上传按钮在左，发送按钮在右 */
  align-items: center;
  margin-top: 12px;
  padding: 0 4px;
  gap: 12px; // 按钮和标签之间的间距

  /* 上传按钮样式优化 */
  :deep(.el-button--text) {
    color: #94a3b8;
    &:hover { color: #764ba2; }
  }

  .file-tag {
    flex: 1; // 让文件名占据剩余空间
    display: flex;
    align-items: center;
    
    :deep(.el-tag) {
      background: rgba(102, 126, 234, 0.1);
      border: 1px solid rgba(102, 126, 234, 0.2);
      color: #4f46e5;
    }
  }
  /* 发送按钮美化 */
  .send-btn {
    width: 36px;
    height: 36px;
    border: none;
    /* 配合你整体的紫色调渐变 */
    background: linear-gradient(135deg, #8798de 0%, #1d3082 100%);
    box-shadow: 0 4px 12px rgba(75, 100, 162, 0.3);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

    &:hover {
      transform: scale(1.1) rotate(-10deg);
      box-shadow: 0 6px 16px rgba(75, 111, 162, 0.4);
    }

    &:active {
      transform: scale(0.95);
    }

    /* 调整图标位置 */
    :deep(.el-icon) {
      font-size: 18px;
      margin-left: 2px; /* 修正纸飞机图标的视觉中心偏差 */
    }
  }
}

/* 顺便优化一下输入框容器，增加整体高级感 */
.input-container {
  background: #ffffff;
  padding: 12px;
  border-radius: 16px;
  border: 1px solid rgba(0, 0, 0, 0.05) !important;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.03);
  transition: border-color 0.3s;

  &:focus-within {
    border-color: #667eea !important;
  }
}


/* AI 加载动效 */
.spinning { animation: rotate 2s linear infinite; }
@keyframes rotate { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

.loading-dots span {
  width: 5px; height: 5px; background: #94a3b8; border-radius: 50%; display: inline-block;
  margin: 0 2px; animation: bounce 1.4s infinite ease-in-out;
  &:nth-child(1) { animation-delay: -0.32s; }
  &:nth-child(2) { animation-delay: -0.16s; }
}
@keyframes bounce { 0%, 80%, 100% { transform: scale(0); } 40% { transform: scale(1); } }

.dashboard-preview-section {
  flex: 0.8;
  .artifact-card {
    height: 100%;
    background: rgba(255,255,255,0.4);
    border-radius: 20px;
    padding: 24px;
    border: 1px solid rgba(255,255,255,0.8);
  }
  .preview-radar-placeholder {
    height: 300px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 2px dashed rgba(0,0,0,0.05);
    border-radius: 20px;
    margin-top: 20px;
    color: #94a3b8;
  }
}

.sub-page { animation: fadeIn 0.4s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }

.dashboard-result-view {
  animation: slideUp 0.6s ease-out; // 向上滑入动画
  padding: 20px;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.artifact-header {
  display: flex;
  justify-content: space-between; /* 🌟 关键：将标题推向左边，数值推向右边 */
  align-items: flex-start;       /* 顶部对齐 */
  margin-bottom: 20px;

  .completion-status {
    text-align: right;           /* 文字向右对齐 */
    
    .percentage {
      display: block;
      font-size: 20px;
      font-weight: 700;
      color: #6366f1;            /* 使用你的主题紫色 */
      line-height: 1;
    }

    .label {
      font-size: 11px;
      color: #94a3b8;            /* 辅助说明文字颜色 */
      margin-top: 4px;
      display: block;
    }
  }
}

/* 看板头部完成度 */
.artifact-card {
  height: 100%; /* 保持容器高度由父级决定，不被内容撑开 */
  display: flex;
  flex-direction: column;
  overflow: hidden; // 确保外层不出现滚动条
}

/* 🌟 核心：滚动区域样式 */
.scroll-container {
  flex: 1; // 自动占满剩余高度
  overflow-y: auto; // 内容超出时显示滚动条
  padding-right: 8px; // 为滚动条留出一点空隙，防止遮挡内容

  /* 美化滚动条 (可选) */
  &::-webkit-scrollbar {
    width: 4px;
  }
  &::-webkit-scrollbar-thumb {
    border-radius: 10px;
  }
  &::-webkit-scrollbar-track {
    background: transparent;
  }
}

/* 保持雷达图有固定高度，不会因为滚动而坍塌 */
.preview-radar-placeholder {
  height: 300px; 
  min-height: 300px;
  width: 100%;
}

/* 核心亮点标签 */
.highlight-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 10px;
  
  .glow-tag {
    border-radius: 6px;
    background: rgba(99, 102, 241, 0.05);
    border: 1px solid rgba(99, 102, 241, 0.2);
    color: #6366f1;
  }
}

/* AI 建议区域 */
.ai-suggestions {
  margin-top: 15px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 12px;
  border-left: 4px solid #6366f1;

  .suggestion-title {
    font-size: 13px;
    font-weight: 600;
    color: #1e293b;
    display: flex;
    align-items: center;
    gap: 5px;
    margin-bottom: 4px;
  }

  .suggestion-text {
    font-size: 12px;
    color: #64748b;
    line-height: 1.5;
    margin: 0;
  }
}

/* 缩小雷达图容器以适应新内容 */
.preview-radar-placeholder {
  height: 260px !important; /* 稍微减小高度给文字腾空间 */
  margin: 10px 0 !important;
}

.dimension-grid {
  display: grid;
  grid-template-columns: 1fr; // 单列布局，如果想两列可以改用 1fr 1fr
  gap: 10px;
  margin-top: 15px;
}

/* 找到 Index.vue 最后的 <style> 部分，替换原本的 .dimension-card 相关样式 */
.dimension-card {
  border-radius: 12px;
  padding: 14px;
  margin-bottom: 10px;
  border: 1px solid transparent;
  transition: all 0.3s ease;

  // 🌟 状态 1：已完善 (绿色)
  &.success {
    background: rgba(16, 185, 129, 0.08); // 浅绿背景
    border-color: rgba(16, 185, 129, 0.2);
    .dim-status { color: #10b981; }
    .dim-desc { color: #065f46; }
  }

  // 🌟 状态 2：不清楚 (橙色)
  &.warning {
    background: rgba(245, 158, 11, 0.08); // 浅橙背景
    border-color: rgba(245, 158, 11, 0.2);
    .dim-status { color: #f59e0b; }
    .dim-desc { color: #92400e; }
  }

  // 🌟 状态 3：未提及 (灰色)
  &.info {
    background: rgba(148, 163, 184, 0.08); // 浅灰背景
    border-color: rgba(148, 163, 184, 0.2);
    .dim-status { color: #64748b; }
    .dim-desc { color: #475569; }
  }

  .dim-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
    
    .dim-name {
      font-size: 14px;
      font-weight: 600;
      color: #1e293b;
    }
    
    .dim-status {
      font-size: 12px;
      font-weight: 700;
    }
  }

  .dim-desc {
    font-size: 12px;
    line-height: 1.5;
    margin: 0;
  }
}

</style>