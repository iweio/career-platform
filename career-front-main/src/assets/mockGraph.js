export const mockGraphData = {
  nodes: [
    { id: 'job_root', name: 'Java开发工程师', label: 'Job', color: '#409EFF', val: 25 },
    { id: 'skill_1', name: 'Spring Boot', label: 'Skill', color: '#67C23A', val: 18 },
    { id: 'skill_2', name: 'Redis', label: 'Skill', color: '#67C23A', val: 16 },
    { id: 'skill_3', name: 'MySQL', label: 'Skill', color: '#67C23A', val: 16 },
    { id: 'skill_4', name: 'JVM调优', label: 'Skill', color: '#E6A23C', val: 14 },
    { id: 'skill_5', name: '微服务架构', label: 'Skill', color: '#E6A23C', val: 14 },
    { id: 'tool_1', name: 'Maven', label: 'Tool', color: '#909399', val: 10 },
    { id: 'tool_2', name: 'Git', label: 'Tool', color: '#909399', val: 10 },
    { id: 'tool_3', name: 'Docker', label: 'Tool', color: '#909399', val: 10 }
  ],
  links: [
    { source: 'job_root', target: 'skill_1' },
    { source: 'job_root', target: 'skill_2' },
    { source: 'job_root', target: 'skill_3' },
    { source: 'job_root', target: 'skill_4' },
    { source: 'job_root', target: 'skill_5' },
    { source: 'skill_1', target: 'tool_1' },
    { source: 'skill_1', target: 'tool_2' },
    { source: 'skill_1', target: 'tool_3' },
    { source: 'skill_5', target: 'skill_1' } // 技能间的关联
  ]
};