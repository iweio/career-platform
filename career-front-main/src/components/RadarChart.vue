<template>
  <div ref="chartRef" style="width: 100%; height: 100%;"></div>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted } from 'vue';
import * as echarts from 'echarts';

const props = defineProps({
  data: { type: Array, default: () => [0,0,0,0,0,0,0,0,0] }
});

const chartRef = ref(null);
let myChart = null;

const initChart = () => {
  if (!chartRef.value) return;
  myChart = echarts.init(chartRef.value);
  const option = {
    radar: {
      // 🌟 核心修改 1：降低半径占比（从默认约 75% 降至 60%），为外圈文字留出空间
      radius: '55%',
      // 🌟 核心修改 2：中心点稍微下移，给顶部文字更多空间
      center: ['50%', '55%'],
      indicator: [
        { name: '专业技能', max: 100 },
        { name: '创新能力', max: 100 },
        { name: '学习能力', max: 100 },
        { name: '实习能力', max: 100 },
        { name: '抗压能力', max: 100 },
        { name: '沟通能力', max: 100 },
        { name: '证书', max: 100 },
      ],
      shape: 'circle',
      splitNumber: 4,
      // 🌟 核心修改 3：通过 padding 确保文字不会紧贴绘图区边缘
      axisName: { 
        color: '#64748b', 
        fontSize: 11,
        padding: [2, 10] 
      },
      splitLine: { lineStyle: { color: 'rgba(0,0,0,0.05)' } },
      splitArea: { show: false }
    },
    series: [{
      type: 'radar',
      data: [{
        value: props.data,
        name: '能力画像',
        areaStyle: {
          color: new echarts.graphic.RadialGradient(0.5, 0.5, 1, [
            { color: 'rgba(102, 126, 234, 0.4)', offset: 0 },
            { color: 'rgba(118, 75, 162, 0.6)', offset: 1 }
          ])
        },
        lineStyle: { color: '#4f46e5', width: 2 },
        itemStyle: { color: '#4f46e5', borderWidth: 0 },
        symbol: 'none'
      }],
      animationDuration: 1200
    }]
  };
  myChart.setOption(option);
};

watch(() => props.data, (newData) => {
  if (myChart) {
    myChart.setOption({ series: [{ data: [{ value: newData }] }] });
  }
}, { deep: true });

onMounted(() => {
  initChart();
  window.addEventListener('resize', () => myChart?.resize());
});

onUnmounted(() => {
  window.removeEventListener('resize', () => myChart?.resize());
  myChart?.dispose();
});
</script>