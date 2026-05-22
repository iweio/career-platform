<template>
  <div ref="graphContainer" class="promotion-graph-canvas"></div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import * as G6 from '@antv/g6'

const props = defineProps({
  jobTitle: { type: String, default: '' },
  paths: { type: Array, default: () => [] },
})

const graphContainer = ref(null)
let graphInstance = null

const formatText = (text, maxLength = 6) => {
  if (!text) return ''
  let result = ''
  for (let i = 0; i < text.length; i += maxLength) {
    result += text.substring(i, i + maxLength) + (i + maxLength < text.length ? '\n' : '')
  }
  return result.trim()
}

const renderChart = () => {
  if (!graphContainer.value) return
  if (!props.paths || props.paths.length === 0) return

  const centerX = (graphContainer.value.scrollWidth || 800) / 2
  const startY = 200
  const nodes = []
  const edges = []

  const startNode = { id: 'start', title: props.jobTitle || '当前岗位' }
  nodes.push({
    id: startNode.id,
    style: {
      type: 'rect', size: [220, 60], x: centerX, y: startY,
      fill: '#E6F4FF', stroke: '#1677FF', lineWidth: 3, radius: 8,
      labelText: formatText(startNode.title, 8),
      labelFill: '#1A1A1A', labelFontSize: 16, labelFontWeight: 'bold',
    },
  })

  const techPaths = props.paths.filter(p => p.type === 'promotion')
  const transferPaths = props.paths.filter(p => p.type === 'transfer')

  transferPaths.forEach((item, index) => {
    const total = transferPaths.length
    const angle = Math.PI + (Math.PI / (total + 1)) * (index + 1)
    const radius = 260
    const label = formatText(item.to, 6)

    nodes.push({
      id: `transfer-${index}`,
      style: {
        type: 'rect', size: [150, label.includes('\n') ? 55 : 40],
        x: centerX + radius * Math.cos(angle),
        y: startY + radius * Math.sin(angle),
        fill: '#F6FFED', stroke: '#B7EB8F', lineDash: [4, 4], radius: 15,
        labelText: label, labelFontSize: 11, labelFill: '#52C41A', labelLineHeight: 14,
      },
    })
    edges.push({
      source: startNode.id, target: `transfer-${index}`,
      style: { stroke: '#B7EB8F', lineDash: [3, 3], endArrow: true, type: 'cubic-vertical' },
    })
  })

  techPaths.forEach((item, idx) => {
    nodes.push({
      id: `promo-${idx}`,
      style: {
        type: 'rect', size: [180, 50],
        x: centerX + 160, y: startY + (idx + 1) * 100,
        fill: '#F0F5FF', stroke: '#597EF7', radius: 6,
        labelText: formatText(item.to, 8), labelFontSize: 12,
      },
    })
    const sId = idx === 0 ? startNode.id : `promo-${idx - 1}`
    edges.push({ source: sId, target: `promo-${idx}`, style: { stroke: '#597EF7', endArrow: true, type: 'cubic-vertical' } })
  })

  if (graphInstance) graphInstance.destroy()
  nextTick(() => {
    graphInstance = new G6.Graph({
      container: graphContainer.value,
      width: graphContainer.value.scrollWidth || 800,
      height: 600,
      data: { nodes, edges },
      layout: undefined,
      behaviors: ['drag-canvas', 'zoom-canvas', 'drag-node'],
      autoFit: 'view',
    })
    graphInstance.render()
  })
}

watch(() => props.paths, () => renderChart(), { deep: true })
onMounted(() => renderChart())
</script>

<style scoped>
.promotion-graph-canvas {
  width: 100%;
  height: 400px;
  background-color: #f8fafc;
  border-radius: 8px;
  overflow: hidden;
  display: block;
}
:deep(canvas) {
  display: block;
  width: 100% !important;
  height: 100% !important;
}
</style>
