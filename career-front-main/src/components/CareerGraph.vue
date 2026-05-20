<template>
  <div class="career-graph-card">
    <div class="graph-header">
      <el-icon><TrendCharts /></el-icon>
      <span>岗位晋升路径参考</span>
    </div>
    <div ref="container" class="graph-container"></div>
    <p class="graph-tip">提示：点击节点查看岗位详情，可缩放拖拽</p>
  </div>
</template>

<script setup>
import { onMounted, ref, onUnmounted } from 'vue'
import { TrendCharts } from '@element-plus/icons-vue'

const container = ref(null)
let graph = null

// 数据定义保持不变
const nodes = [
  { id: 'game_op', label: '运营专员' },
  { id: 'senior_op', label: '资深运营' },
  { id: 'op_expert', label: '专家' },
  { id: 'op_leader', label: '组长' },
  { id: 'op_supervisor', label: '主管' },
  { id: 'op_manager', label: '经理' },
  { id: 'op_director', label: '总监' },
  { id: 'game_producer', label: '制作人' },
]

const edges = [
  { source: 'game_op', target: 'senior_op' },
  { source: 'senior_op', target: 'op_expert' },
  { source: 'senior_op', target: 'op_leader' },
  { source: 'op_leader', target: 'op_supervisor' },
  { source: 'op_supervisor', target: 'op_manager' },
  { source: 'op_manager', target: 'op_director' },
  { source: 'op_director', target: 'game_producer' },
]

onMounted(async () => {
  // 动态引入 G6
  const G6Module = await import('https://gw.alipayobjects.com/os/antv/pkg/_antv.g6-4.8.12/build/g6.min.js')
  const G6 = G6Module.default

  graph = new G6.Graph({
    container: container.value,
    width: container.value.clientWidth,
    height: 350, // 减小高度以适配侧边栏
    layout: {
      type: 'dagre',
      rankdir: 'LR', // 🌟 改为从左往右，更适合侧边栏窄屏显示
      nodesep: 20,
      ranksep: 40,
    },
    defaultNode: {
      type: 'rect',
      size: [80, 30],
      style: {
        fill: '#f0f7ff',
        stroke: '#409EFF',
        lineWidth: 1,
        radius: 6,
      },
      labelCfg: {
        style: { fill: '#409EFF', fontSize: 11 },
      },
    },
    defaultEdge: {
      style: {
        stroke: '#d1d5db',
        endArrow: { path: G6.Arrow.triangle(5, 8, 0), fill: '#d1d5db' },
      },
    },
    modes: { default: ['drag-canvas', 'zoom-canvas'] },
  })

  graph.data({ nodes, edges })
  graph.render()
})

// 销毁时清理防止内存泄漏
onUnmounted(() => {
  if (graph) graph.destroy()
})
</script>

<style scoped lang="scss">
.career-graph-card {
  margin-top: 24px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 16px;
  border: 1px solid #edf2f7;
  padding: 16px;

  .graph-header {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 12px;
    .el-icon { color: #409EFF; }
  }

.graph-container {
  background: radial-gradient(circle at center, #daf9fec9 0%, #f4f7e05f 100%);
  /* 如果是深色模式 */
  /* background: radial-gradient(circle at center, #1a1a2e 0%, #0f0f1b 100%); */
}

  .graph-tip {
    font-size: 11px;
    color: #94a3b8;
    margin-top: 8px;
    text-align: center;
  }
}
</style>