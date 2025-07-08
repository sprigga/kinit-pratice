import { EChartsOption } from 'echarts'
import { useI18n } from '@/hooks/web/useI18n'

const { t } = useI18n()

export const newCustomerlineOptions: EChartsOption = {
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
    boundaryGap: true,
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
    data: ['新增客户'],
    bottom: -5
  },
  series: [
    {
      name: '新增客户',
      smooth: false, // true 有弧度 ，false 没弧度（直線）
      symbol: 'circle', // 將小圓點改成實心 不寫symbol默認空心
      symbolSize: 8, // 小圓點的大小
      type: 'line',
      data: [100, 120, 161, 134, 105, 160, 165, 114, 163, 185, 118, 123],
      animationDuration: 2800,
      animationEasing: 'quadraticOut',
      itemStyle: {
        color: 'rgba(79,168,249)' // 整体颜色
      },
      lineStyle: {
        width: 1, //設置線條粗细
        opacity: 1
      }
    }
  ]
}

export const memberPieOptions: EChartsOption = {
  tooltip: {
    trigger: 'item',
    formatter: '{a} <br/>{b} : {c} ({d}%)'
  },
  series: [
    {
      name: '各樓層銷售情況统計',
      type: 'pie',
      radius: '60%',
      center: ['50%', '50%'],
      data: [
        { value: 335, name: '青铜卡' },
        { value: 310, name: '白银卡' },
        { value: 234, name: '黄金卡' },
        { value: 135, name: '鑽石卡' }
      ]
    }
  ]
}

export const customerConversionLineOptions: EChartsOption = {
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
    boundaryGap: true,
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
    data: ['轉換次數', '轉換率'],
    bottom: -5
  },
  series: [
    {
      name: '轉換次數',
      smooth: false, // true 有弧度 ，false 没弧度（直線）
      symbol: 'circle', // 將小圓點改成實心 不寫symbol默認空心
      symbolSize: 8, // 小圓點的大小
      type: 'line',
      data: [100, 120, 161, 134, 105, 160, 165, 114, 163, 185, 118, 123],
      animationDuration: 2800,
      animationEasing: 'quadraticOut',
      itemStyle: {
        color: 'rgba(110,199,30)' // 整体颜色
      },
      lineStyle: {
        width: 1, //設置線條粗细
        opacity: 1
      }
    },
    {
      name: '轉換率',
      smooth: false, // true 有弧度 ，false 没弧度（直線）
      symbol: 'circle', // 將小圓點改成實心 不寫symbol默認空心
      symbolSize: 8, // 小圓點的大小
      type: 'line',
      data: [120, 82, 91, 154, 162, 140, 145, 250, 134, 56, 99, 123],
      animationDuration: 2800,
      animationEasing: 'quadraticOut',
      itemStyle: {
        color: 'rgba(79,168,249)' // 整体颜色
      },
      lineStyle: {
        width: 1, //設置線條粗细
        opacity: 1
      }
    }
  ]
}

export const paySuccesslineOptions: EChartsOption = {
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
    boundaryGap: true,
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
    data: ['支付成功客户數'],
    bottom: -5
  },
  series: [
    {
      name: '支付成功客户數',
      smooth: false, // true 有弧度 ，false 没弧度（直線）
      symbol: 'circle', // 將小圓點改成實心 不寫symbol默認空心
      symbolSize: 8, // 小圓點的大小
      type: 'line',
      data: [100, 120, 161, 134, 105, 160, 165, 114, 163, 185, 118, 123],
      animationDuration: 2800,
      animationEasing: 'quadraticOut',
      itemStyle: {
        color: 'rgba(79,168,249)' // 整体颜色
      },
      lineStyle: {
        width: 1, //設置線條粗细
        opacity: 1
      }
    }
  ]
}
