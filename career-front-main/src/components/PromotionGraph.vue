<template>
  <div ref="graphContainer" class="promotion-graph-canvas"></div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue';
import * as G6 from '@antv/g6';

const props = defineProps({
  // 接收父组件传来的岗位名称，例如 "Java"
  jobTitle: {
    type: String,
    default: ''
  }
});

const graphContainer = ref(null);
let graphInstance = null;

// 【自动化关键】动态导入 promotion 文件夹下的所有 JSON
const promotionModules = import.meta.glob('@/mock/promotion/*.json', { eager: true });

const renderChart = async () => {
  if (!graphContainer.value || !props.jobTitle) return;

  // --- 1. 映射逻辑 (请根据你的实际岗位补全映射) ---
  const nameMap = {
    '游戏运营':'game_operation_engineer',
    '科研人员':'researcher',
    '技术支持工程师':'technical_support_engineer',
    'C/C++':'cpp',
    '硬件测试':'hardware_test',
    '软件测试':'software_test_special',
    '前端开发':'frontend',
    '实施工程师':'implementation_engineer',
    '测试工程师':'test_engineer'
  };

  const targetName = props.jobTitle;
  const targetKey = nameMap[targetName] || targetName.toLowerCase();
  
  let rawData = null;
  let dynamicFileName = "";

  for (const path in promotionModules) {
    const fileName = path.split('/').pop().replace('.json', '').toLowerCase();
    if (targetKey.includes(fileName) || fileName.includes(targetKey)) {
      rawData = promotionModules[path].default || promotionModules[path];
      dynamicFileName = fileName;
      break;
    }
  }

  if (!rawData) return;

  // --- 2. 文字智能换行助手 ---
  const formatText = (text, maxLength = 6) => {
    if (!text) return "";
    let result = "";
    for (let i = 0; i < text.length; i += maxLength) {
      result += text.substring(i, i + maxLength) + (i + maxLength < text.length ? "\n" : "");
    }
    return result.trim();
  };

  const promotionList = rawData[`${dynamicFileName}_promotion_routes`] || [];
  const transferList = rawData[`${dynamicFileName}_transfer_routes`] || [];
  const nodes = [];
  const edges = [];

  // --- 3. 坐标计算基础值 (防止图表消失的关键) ---
  const centerX = (graphContainer.value?.scrollWidth || 800) / 2;
  const startY = 280; 

  const startJob = promotionList.find(i => i.level === 1) || promotionList[0];
  const techPath = promotionList.filter(i => i.route_type === 'technical' && i.level !== 1);
  const mgmtPath = promotionList.filter(i => i.route_type === 'management');

  // --- 4. 绘制中心节点 ---
  nodes.push({
    id: `promo-${startJob.id}`,
    style: {
      type: 'rect',
      size: [220, 60],
      x: centerX,
      y: startY,
      fill: '#E6F4FF', 
      stroke: '#1677FF',
      lineWidth: 3,
      radius: 8,
      labelText: formatText(startJob.title, 8), // 允许稍长
      labelFill: '#1A1A1A',
      labelFontSize: 16,
      labelFontWeight: 'bold',
    }
  });

  // --- 5. 绘制换岗节点 (带换行逻辑) ---
  transferList.forEach((item, index) => {
    const total = transferList.length;
    const angle = Math.PI + (Math.PI / (total + 1)) * (index + 1);
    const radius = 260; // 足够宽的间距
    
    const formattedName = formatText(item.post_name, 6); // 每6个字换行

    nodes.push({
      id: `transfer-${item.id}`,
      style: {
        type: 'rect',
        size: [150, formattedName.includes('\n') ? 55 : 40], // 自动撑高
        x: centerX + radius * Math.cos(angle),
        y: startY + radius * Math.sin(angle),
        fill: '#F6FFED',
        stroke: '#B7EB8F',
        lineDash: [4, 4],
        radius: 15,
        labelText: formattedName,
        labelFontSize: 11,
        labelFill: '#52C41A',
        labelLineHeight: 14
      }
    });

    edges.push({
      source: `promo-${startJob.id}`,
      target: `transfer-${item.id}`,
      style: { stroke: '#B7EB8F', lineDash: [3, 3], endArrow: true, type: 'cubic-vertical' }
    });
  });

  // --- 6. 绘制晋升双轨 ---
  // 技术路线
  techPath.forEach((item, idx) => {
    nodes.push({
      id: `promo-${item.id}`,
      style: {
        type: 'rect',
        size: [180, 50],
        x: centerX + 160,
        y: startY + (idx + 1) * 100,
        fill: '#F0F5FF',
        stroke: '#597EF7',
        radius: 6,
        labelText: formatText(item.title, 8),
        labelFontSize: 12,
      }
    });
    const sId = idx === 0 ? `promo-${startJob.id}` : `promo-${techPath[idx-1].id}`;
    edges.push({ source: sId, target: `promo-${item.id}`, style: { stroke: '#597EF7', endArrow: true, type: 'cubic-vertical' } });
  });

  // 管理路线
  mgmtPath.forEach((item, idx) => {
    nodes.push({
      id: `promo-${item.id}`,
      style: {
        type: 'rect',
        size: [180, 50],
        x: centerX - 160,
        y: startY + (idx + 1) * 100,
        fill: '#FFFBE6',
        stroke: '#FAAD14',
        radius: 6,
        labelText: formatText(item.title, 8),
        labelFontSize: 12,
      }
    });
    const sId = idx === 0 ? `promo-${startJob.id}` : `promo-${mgmtPath[idx-1].id}`;
    edges.push({ source: sId, target: `promo-${item.id}`, style: { stroke: '#FAAD14', lineDash: [3, 3], endArrow: true, type: 'cubic-vertical' } });
  });

  // --- 7. 执行渲染 ---
  if (graphInstance) graphInstance.destroy();
  await nextTick();

  graphInstance = new G6.Graph({
    container: graphContainer.value,
    width: graphContainer.value.scrollWidth,
    height: 800,
    data: { nodes, edges },
    layout: undefined, 
    behaviors: ['drag-canvas', 'zoom-canvas', 'drag-node'],
    autoFit: 'view',
  });

  graphInstance.render();
};
onMounted(() => renderChart());

// 当切换岗位时，重新画图
watch(() => props.jobTitle, () => renderChart());
</script>

<style scoped>
.promotion-graph-canvas {
  width: 100%;
  height: 400px; /* 固定高度或者 min-height */
  background-color: #f8fafc;
  border-radius: 8px;
  overflow: hidden; /* 防止 canvas 溢出 */
  display: block;   /* 确保是块级元素 */
}

/* 强制清除 G6 自动生成的内部 margin */
:deep(canvas) {
  display: block;
  width: 100% !important;
  height: 100% !important;
}


</style>