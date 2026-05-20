<template>
  <div class="report-export-page fade-in">
    <div class="main-layout glass-card">
      
      <div class="report-display-container" v-loading="pageLoading">
        <div class="paper-header">
          <input v-model="reportData.reportTitle" class="title-input" :readonly="!isEditing" />
          <div class="paper-meta">最后更新：{{ lastUpdateTime }} | 导师：AI Career Pilot</div>
        </div>
        
        <div class="paper-body">
          <el-input
            v-model="reportContent"
            type="textarea"
            :autosize="{ minRows: 22 }"
            :readonly="!isEditing"
            class="article-editor"
            placeholder="正在生成报告内容..."
          />
        </div>
      </div>

      <div class="control-panel">
        <div class="ai-assistant-box shadow-sm">
          <div class="panel-label">
            <el-icon><MagicStick /></el-icon> 智能润色指令
          </div>
          
          <div class="instruction-input-wrapper">
            <el-input
              v-model="polishNote"
              type="textarea"
              :rows="3"
              placeholder="输入修改要求，例如：'突出我的架构设计能力'..."
              resize="none"
            />
            <div class="input-footer">
              <el-button 
                type="primary" 
                @click="handleAIPolish" 
                :loading="polishing"
                round
                size="small"
                class="execute-btn"
              >
                <el-icon><Promotion /></el-icon> 执行润色
              </el-button>
            </div>
          </div>

          <div class="quick-tags">
            <el-tag v-for="tag in ['更专业', '更精简', '突出技术', '润色摘要']" 
                    :key="tag" @click="polishNote = tag" class="tag-item">
              {{ tag }}
            </el-tag>
          </div>
        </div>

        <div class="history-module">
          <div class="panel-label">
            <div class="label-left">
              <el-icon><Clock /></el-icon> 润色历史记录
            </div>
            <el-tooltip content="还原前会自动备份当前版本">
              <el-icon class="info-icon"><QuestionFilled /></el-icon>
            </el-tooltip>
          </div>
          
          <div class="history-list-container">
            <div v-if="polishHistory.length === 0" class="empty-history">
              <el-icon><InfoFilled /></el-icon> 暂无润色记录
            </div>
            
            <div 
              v-for="(item, index) in polishHistory" 
              :key="index" 
              class="history-card"
              @click="restoreVersion(item)"
            >
              <div class="card-top">
                <span class="version-tag" :class="item.type === 'user' ? 'type-user' : 'type-ai'">
                  {{ item.type === 'user' ? '手动快照' : 'AI 润色' }}
                </span>
                <span class="time">{{ item.time }}</span>
              </div>
              <p class="history-note">“{{ item.note }}”</p>
              <div class="hover-mask">
                <el-icon><RefreshLeft /></el-icon> 切换到此版本
              </div>
            </div>
          </div>
        </div>

        <div class="action-group">
          <el-button :type="isEditing ? 'warning' : 'default'" class="wide-btn" @click="toggleEdit">
            <el-icon><EditPen v-if="!isEditing" /><Checked v-else /></el-icon>
            {{ isEditing ? '保存修改' : '进入手动编辑' }}
          </el-button>

          <el-button type="success" class="wide-btn download-btn" @click="handleDownload" :loading="downloadLoading">
            <el-icon><Download /></el-icon> 导出 PDF 最终版
          </el-button>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue' // 添加 onMounted
import { ElMessage, ElNotification } from 'element-plus'
import { 
  MagicStick, EditPen, Download, Promotion, 
  Checked, Clock, InfoFilled, RefreshLeft, QuestionFilled 
} from '@element-plus/icons-vue'
import html2pdf from 'html2pdf.js';

const props = defineProps({
  reportData: {
    type: Object,
    default: () => ({
      reportTitle: '2026 前端开发工程师成长规划报告',
initialContent: `职业进阶学习计划：Java 高级架构师之路

第一阶段：Java 核心深化与架构基础 (2-3个月)
核心目标：深化 JVM 与并发编程，掌握微服务分布式核心体系。
- 学习重点：JUC 并发工具包、JVM 垃圾回收调优、Spring Cloud Alibaba (Nacos/Sentinel)、消息中间件原理 (Kafka)。
- 推荐资源：《深入理解Java虚拟机》、极客时间《Java并发编程实战》。

第二阶段：性能调优与云原生技术栈 (2-3个月)
核心目标：掌握大规模系统调优，熟练运用 K8s 进行容器化运维。
- 学习重点：MySQL 索引与 SQL 调优、Redis 集群方案、Kubernetes 编排、Prometheus 可观测性监控。
- 推荐资源：《高性能MySQL》、腾讯云/阿里云 K8s 实战练习。

第三阶段：领域驱动设计 (DDD) 与架构演进 (1-2个月)
核心目标：掌握复杂业务建模方法，建立整洁架构思维。
- 学习重点：限界上下文划分、聚合根设计、六边形架构、代码重构与设计模式深度应用。
- 推荐资源：《领域驱动设计：软件核心复杂性应对之道》、Martin Fowler 博客。

第四阶段：综合实战与软技能提升 (持续进行)
核心目标：提升技术方案评审、团队协作及全栈项目主导能力后。
- 学习重点：编写高质量技术设计方案、敏捷开发管理 (Jira)、跨团队沟通、技术影响力建设 (博客/开源)。
- 推荐资源：《代码大全》、《人月神话》。`
    })
  }
})

const pageLoading = ref(true) // 初始状态为加载中
const reportContent = ref('') // 先设为空，加载完再赋值

onMounted(() => {
  // 模拟报告生成的加载时间，例如 1.2 秒
  setTimeout(() => {
    reportContent.value = props.reportData.initialContent
    pageLoading.value = false
    ElMessage({
      message: '职业规划报告已生成',
      type: 'success',
      plain: true,
    })
  }, 3000)
})

// 状态管理
const polishNote = ref('')
const isEditing = ref(false)
const polishing = ref(false)
const downloadLoading = ref(false)
const lastUpdateTime = ref(new Date().toLocaleTimeString())




// 历史记录数据
const polishHistory = ref([])

// 逻辑：执行润色并存入历史
const handleAIPolish = () => {
  if (!polishNote.value) return ElMessage.warning('请输入润色要求')
  polishing.value = true
  
  setTimeout(() => {
    // 1. 存档当前内容
    polishHistory.value.unshift({
      note: polishNote.value,
      content: reportContent.value,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      type: 'ai'
    })

    // 2. 模拟覆盖
reportContent.value = `第1阶段: Java核心技术深化与架构基础
⏰ 时间范围: 2个月

🎯 核心目标: 精通Java并发与JVM调优，掌握Spring Cloud微服务核心组件与分布式理论。

📚 学习内容:
Java并发编程与JVM调优
Spring Boot/Cloud微服务架构
分布式系统理论与消息中间件

📖 推荐资源:
《Java并发编程的艺术》
《深入理解Java虚拟机》
极客时间相关课程
Spring Cloud Alibaba官方文档
简易电商微服务实践项目

第2阶段: 高并发系统与云原生
⏰ 时间范围: 2个月

🎯 核心目标: 掌握数据库与缓存高级优化，熟练使用Docker/Kubernetes进行云原生部署与运维。

📚 学习内容:
MySQL优化与Redis深度应用
Docker与Kubernetes容器化编排
系统监控(如Prometheus/Grafana)与设计方法论

📖 推荐资源:
《高性能MySQL》
《Redis设计与实现》
极客时间《Kubernetes实战》
云平台动手实验
研究优秀开源项目架构

第3阶段: 架构设计与技术视野
⏰ 时间范围: 1个月

🎯 核心目标: 理解领域驱动设计(DDD)与整洁架构，跟踪技术趋势并开始建立技术影响力。

📚 学习内容:
领域驱动设计(DDD)核心思想
整洁/六边形架构
代码重构与设计模式
前沿技术趋势跟踪

📖 推荐资源:
《领域驱动设计》
Martin Fowler博客
参与技术社区
用DDD思想重构一个项目

第4阶段: 综合实践与职业发展
⏰ 时间范围: 持续进行

🎯 核心目标: 通过实战项目整合技术栈，提升团队协作、技术方案设计与评审等软技能。

📚 学习内容:
主导或深度参与复杂全栈项目
技术方案设计与评审
项目管理与跨团队沟通
技术面试与招聘知识

📖 推荐资源:
主动承担复杂工作或发起开源项目
《代码大全》、《人月神话》
进行技术分享
模拟方案评审与面试`;
    
    polishing.value = false;
    polishNote.value = '';
    lastUpdateTime.value = new Date().toLocaleTimeString();
    
    ElNotification({
      title: '润色完成',
      message: '旧版本已存入历史，可随时切换回滚',
      type: 'success',
      position: 'bottom-right'
    });
  }, 1000)
}

// 逻辑：还原版本（含双向备份）
const restoreVersion = (item) => {
  // 1. 获取当前屏幕上的“即将被覆盖”的内容作为快照
  const currentSnapshot = {
    note: "还原前的当前版本",
    content: reportContent.value,
    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    type: 'user' // 绿色标签标记
  };

  // 2. 从历史列表中移除要还原的那一项
  const index = polishHistory.value.indexOf(item);
  if (index > -1) {
    polishHistory.value.splice(index, 1);
  }

  // 3. 将当前快照压入历史顶部
  polishHistory.value.unshift(currentSnapshot);

  // 4. 更新正文
  reportContent.value = item.content;
  lastUpdateTime.value = new Date().toLocaleTimeString();
  
  ElMessage.info('已切换版本，原内容已自动备份');
}

const toggleEdit = () => {
  isEditing.value = !isEditing.value
  if (!isEditing.value) ElMessage.success('手动修改已保存')
}

const handleDownload = () => {
  // 1. 开启加载状态
  downloadLoading.value = true;

  // 2. 抓取左侧报告容器（即包含标题和正文的那块区域）
  const element = document.querySelector('.report-display-container');

  if (!element) {
    ElMessage.error('未找到报告内容');
    downloadLoading.value = false;
    return;
  }

  // 3. 配置导出参数
  const opt = {
    margin: [10, 10], // 上下左右边距
    filename: `${props.reportData.reportTitle || '职业规划报告'}.pdf`,
    image: { type: 'jpeg', quality: 0.98 },
    html2canvas: { 
      scale: 2, // 提高清晰度，解决模糊问题
      useCORS: true, 
      letterRendering: true 
    },
    jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
  };

  // 4. 执行导出
  html2pdf()
    .set(opt)
    .from(element)
    .save()
    .then(() => {
      downloadLoading.value = false;
      ElMessage.success('PDF 导出成功');
    })
    .catch((err) => {
      console.error('导出失败:', err);
      downloadLoading.value = false;
      ElMessage.error('导出失败，请重试');
    });
};
</script>

<style scoped lang="scss">
.report-export-page {
  height: 90vh;
  padding: 20px;
  display: flex;
  justify-content: center;
  background: #f4f7fa;

  .main-layout {
    display: grid;
    grid-template-columns: 1fr 340px;
    gap: 20px;
    width: 100%;
    max-width: 1260px;
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(20px);
    border-radius: 24px;
    padding: 24px;
    border: 1px solid rgba(255, 255, 255, 0.5);
  }
}

.report-display-container {
  background: #fff8e739;;
  border-radius: 16px;
  padding: 40px 50px;
  overflow-y: auto;
  border: 1px solid #eef2f6;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.02);

  .paper-header {
    margin-bottom: 25px;
    border-bottom: 1px solid #f1f5f9;
    padding-bottom: 15px;
    .title-input {
      border: none; outline: none; font-size: 26px; font-weight: bold; width: 100%; color: #1e293b;
      background: transparent;
    }
    .paper-meta { font-size: 12px; color: #94a3b8; margin-top: 5px; }
  }

  .article-editor {
    :deep(.el-textarea__inner) {
      border: none !important; box-shadow: none !important;
      padding: 0; font-size: 16px; line-height: 1.8; color: #334155;
      background: transparent;
    }
  }
}

.control-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: 100%;
  overflow: hidden;

  /* 🌟 修正：统一 ai-assistant-box 样式，确保毛玻璃生效 */
  .ai-assistant-box {
    flex-shrink: 0;
    background: rgba(255, 255, 255, 0.2) !important; // 极高的透明度
    backdrop-filter: blur(12px) saturate(180%) !important;
    padding: 20px !important;
    border-radius: 20px !important;
    border: 1px solid rgba(255, 255, 255, 0.4) !important; // 强调白色边缘
    box-shadow: none !important; // 去掉沉重的阴影
    margin-bottom: 0; // 移除多余间距

    /* 🌟 核心修改：输入框包装器模拟图一的纯白悬浮感 */
    .instruction-input-wrapper {
      background: #ffffff !important; // 改为纯白
      border-radius: 12px;
      padding: 12px;
      border: none !important; // 移除图二看到的灰色边框
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04) !important; // 极淡阴影增加层级
      
      :deep(.el-textarea__inner) {
        border: none !important;
        box-shadow: none !important;
        background: transparent !important;
        padding: 0;
        font-size: 13px;
        color: #475569;
        &::placeholder { color: #cbd5e1; }
      }

      .input-footer {
        display: flex;
        justify-content: flex-end;
        margin-top: 8px;
      }
    }
  }

  .panel-label {
    font-size: 14px;
    font-weight: bold;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    justify-content: flex-start;
    gap: 8px;
    color: #475569;
    .el-icon { color: #70a1ff; }
    .info-icon { color: #cbd5e1; font-size: 14px; cursor: help; }
  }

  .execute-btn {
    background: linear-gradient(135deg, #fffdea56 0%, #f5f5f8 100%) !important;
    border: none !important;
    color: rgb(12, 25, 66) !important;
    font-weight: 600;
    box-shadow: 0 4px 15px rgba(129, 140, 248, 0.15) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(129, 140, 248, 0.3) !important;
      filter: brightness(1.05);
    }
  }

  .history-module {
    flex: 1;
    background: rgba(255, 255, 255, 0.2) !important; // 极高的透明度
    padding: 18px;
    border-radius: 16px;
    border: 1px solid #eef2f6;
    display: flex;
    flex-direction: column;
    overflow: hidden;

    .history-list-container {
      flex: 1;
      overflow-y: auto;
      padding-right: 4px;

      .history-card {
        background: #b1bcc11f;
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 10px;
        cursor: pointer;
        position: relative;
        transition: 0.3s;
        border: 1px solid transparent;

        &:hover {
          background: #f0f7ff;
          border-color: #70a1ff;
          .hover-mask { opacity: 1; }
        }

        .card-top {
          display: flex;
          justify-content: space-between;
          margin-bottom: 6px;
          .version-tag {
            font-size: 10px; font-weight: bold; padding: 2px 6px; border-radius: 4px;
            &.type-ai { background: rgba(112, 161, 255, 0.1); color: #70a1ff; }
            &.type-user { background: rgba(16, 185, 129, 0.1); color: #10b981; }
          }
          .time { font-size: 10px; color: #94a3b8; }
        }

        .history-note { font-size: 12px; color: #080808; margin: 0; text-overflow: ellipsis; overflow: hidden; white-space: nowrap; }

        .hover-mask {
          position: absolute; inset: 0; background: rgba(205, 228, 238, 0.61);
          border-radius: 10px; display: flex; align-items: center; justify-content: center;
          color: rgb(18, 51, 111); font-size: 12px; font-weight: bold; gap: 5px; opacity: 0; transition: 0.3s;
          border: 1px solid #2a3242b2;
        }
      }
    }
  }

  .quick-tags {
    margin: 12px 0;
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    .tag-item {
      border: 1px solid transparent !important;
      padding: 4px 12px !important;
      font-weight: 500;
      border-radius: 8px !important;
      transition: all 0.2s !important;
      &:nth-child(1) { background: rgba(165, 220, 252, 0.185) !important; color: #262626 !important; }
      &:nth-child(2) { background: rgba(253, 181, 230, 0.1) !important; color: #262626 !important; }
      &:nth-child(3) { background: rgba(198, 238, 198, 0.161) !important; color: #262626 !important; }
      &:nth-child(4) { background: rgba(253, 186, 116, 0.1) !important; color: #262626 !important; }
      &:hover { background: #ffffff !important; border-color: currentColor !important; transform: scale(1.05); }
    }
  }

  .action-group {
    flex-shrink: 0;
    display: flex;
    flex-direction: column;
    gap: 10px;
    width: 100%;
    align-items: center;
    box-sizing: border-box;
  }
}

.wide-btn {
  background: linear-gradient(135deg, #f2fbfd 0%, #e6f7fc5d 100%) !important;
  border: 1.5px dashed #e2e8f0 !important;
  color: rgb(74, 72, 72) !important;
  width: 100% !important;
  max-width: 320px;
  height: 48px !important;
  margin: 0 !important;
  border-radius: 12px !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  box-sizing: border-box !important;
  font-weight: bold;
  font-size: 14px;
  box-sizing: border-box;
  padding: 0 20px !important;
  .el-icon { margin-right: 8px; font-size: 16px; }
  &:hover {
    border-style: solid !important;
    border-color: #113354 !important;
    color: #0e2857 !important;
    background: white !important;
  }
}

.download-btn {
  margin: 0 !important;
  background: linear-gradient(135deg, #f2fbfd 0%, #e6f7fc5d 100%) !important;
  color: rgb(74, 72, 72) !important;
  font-weight: bold;
  box-shadow: 0 6px 18px rgba(45, 212, 191, 0.15) !important;
  &:hover { box-shadow: 0 8px 25px rgba(45, 212, 191, 0.25) !important; filter: saturate(1.1); }
}

.fade-in { animation: fadeIn 0.6s ease-out; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
</style>