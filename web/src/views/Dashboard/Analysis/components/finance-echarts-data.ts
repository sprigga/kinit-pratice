import { EChartsOption } from 'echarts'
import { useI18n } from '@/hooks/web/useI18n'

const { t } = useI18n()

export const line2Options: EChartsOption = {
  xAxis: {
    data: [
      t('analysis.january'),
      t('analysis.february'),
      t('analysis.march'),
      t('analysis.april'),
      t('analysis.may'),
      t('analysis.june'),
      t('analysis.july'),
      t('analysis.august'),
      t('analysis.september'),
      t('analysis.october'),
      t('analysis.november'),
      t('analysis.december')
    ],
    boundaryGap: false,
    axisTick: {
      show: false // 不限制坐標刻度
    }
  },
  grid: {
    left: 20,
    right: 20,
    bottom: 35,
    top: 30,
    containLabel: true
  },
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'cross'
    },
    padding: [5, 10]
  },
  yAxis: {
    type: 'value',
    axisTick: {
      show: false // 不限制坐標刻度
    }
  },
  legend: {
    data: ['銷售額', '充值金額'],
    bottom: -5
  },
  series: [
    {
      name: '銷售額',
      smooth: false, // true 有弧度 ，false 没弧度（直線）
      symbol: 'circle', // 將小圓點改成實心 不寫symbol默認空心
      symbolSize: 8, // 小圓點的大小
      type: 'line',
      data: [86423, 74129, 57231, 62547, 87345, 92856, 64123, 51237, 95874, 73019, 58642, 69428],
      animationDuration: 2800,
      animationEasing: 'quadraticOut',
      itemStyle: {
        color: 'rgba(110,199,30)' // 整体颜色
      },
      lineStyle: {
        width: 1, //設置線條粗细
        opacity: 1
      },
      areaStyle: {
        color: 'rgba(110,199,30, 0.2)' // 區域填充颜色
      }
    },
    {
      name: '充值金額',
      smooth: false, // true 有弧度 ，false 没弧度（直線）
      symbol: 'circle', // 將小圓點改成實心 不寫symbol默認空心
      symbolSize: 8, // 小圓點的大小
      type: 'line',
      data: [95874, 86423, 87345, 74129, 73019, 62547, 69428, 57231, 64123, 58642, 92856, 51237],
      animationDuration: 2800,
      animationEasing: 'quadraticOut',
      itemStyle: {
        color: 'rgba(79,168,249)' // 整体颜色
      },
      lineStyle: {
        width: 1, //設置線條粗细
        opacity: 1
      },
      areaStyle: {
        color: 'rgba(79,168,249, 0.2)' // 區域填充颜色
      }
    }
  ]
}

export const lineOptions: EChartsOption = {
  xAxis: {
    data: [
      t('analysis.january'),
      t('analysis.february'),
      t('analysis.march'),
      t('analysis.april'),
      t('analysis.may'),
      t('analysis.june'),
      t('analysis.july'),
      t('analysis.august'),
      t('analysis.september'),
      t('analysis.october'),
      t('analysis.november'),
      t('analysis.december')
    ],
    boundaryGap: false,
    axisTick: {
      show: false // 不限制坐標刻度
    }
  },
  grid: {
    left: 20,
    right: 20,
    bottom: 35,
    top: 30,
    containLabel: true
  },
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'cross'
    },
    padding: [5, 10]
  },
  yAxis: {
    type: 'value',
    axisTick: {
      show: false // 不限制坐標刻度
    }
  },
  legend: {
    data: ['服飾', '電器', '茶葉', '珠寶', '家紡', '玩具'],
    bottom: -5
  },
  series: [
    {
      name: '服飾',
      smooth: false, // true 有弧度 ，false 没弧度（直線）
      type: 'line',
      data: [60384, 74218, 57149, 83297, 21675, 96743, 38547, 72436, 93742, 59073, 81394, 66912],
      animationDuration: 2800,
      animationEasing: 'quadraticOut'
    },
    {
      name: '電器',
      smooth: false, // true 有弧度 ，false 没弧度（直線）
      type: 'line',
      data: [29541, 64783, 79942, 50472, 91374, 26819, 69247, 78354, 48672, 81124, 92038, 36847]
    },
    {
      name: '茶葉',
      smooth: false, // true 有弧度 ，false 没弧度（直線）
      type: 'line',
      data: [84273, 73842, 21675, 97342, 65938, 82473, 59172, 40672, 92438, 76592, 83947, 50283]
    },
    {
      name: '珠寶',
      smooth: false, // true 有弧度 ，false 没弧度（直線）
      type: 'line',
      data: [21675, 84273, 50283, 76924, 68574, 92438, 39572, 93742, 50472, 78354, 59247, 92038]
    },
    {
      name: '家紡',
      smooth: false, // true 有弧度 ，false 没弧度（直線）
      type: 'line',
      data: [78354, 76924, 82473, 50472, 48672, 65938, 64783, 50283, 73842, 40672, 84273, 76592]
    },
    {
      name: '玩具',
      smooth: false, // true 有弧度 ，false 没弧度（直線）
      type: 'line',
      data: [40672, 50472, 59247, 81394, 36847, 59273, 26819, 66912, 59172, 84273, 50283, 76924]
    }
  ]
}

export const pieOptions: EChartsOption = {
  tooltip: {
    trigger: 'item',
    formatter: '{a} <br/>{b} : {c} ({d}%)'
  },
  series: [
    {
      name: '各品類銷售額情況统計',
      type: 'pie',
      radius: '55%',
      center: ['50%', '40%'],
      data: [
        { value: 599999, name: '服飾' },
        { value: 89999, name: '電器' },
        { value: 219879, name: '茶葉' },
        { value: 897999, name: '珠寶' },
        { value: 102999, name: '家紡' },
        { value: 499090, name: '玩具' }
      ]
    }
  ]
}
