<script setup>
import { ref } from 'vue'
import { propTypes } from '@/utils/propTypes'

const props = defineProps({
  expression: propTypes.string.def('')
})

let dateArr = []
let isShow = false
let dayRule = ''
let dayRuleSup = ''
let resultList = []

/**
 * 計算 Cron 表達式最近五次運行時間结果
 * 感谢若依：http://vue.ruoyi.vip/monitor/job
 */
const expressionChange = (expression) => {
  // 計算開始-隱藏结果
  isShow = false
  // 獲取规则數组[0秒、1分、2時、3日、4月、5星期、6年]
  let ruleArr = expression.split(' ')
  // 用于計錄進入循環的次數
  let nums = 0
  // 用于暂時存符號時間规则结果的數组
  let resultArr = []
  // 獲取當前時間精確至[年、月、日、時、分、秒]
  let nTime = new Date()
  let nYear = nTime.getFullYear()
  let nMonth = nTime.getMonth() + 1
  let nDay = nTime.getDate()
  let nHour = nTime.getHours()
  let nMin = nTime.getMinutes()
  let nSecond = nTime.getSeconds()
  // 根據规则獲取到近100年可能年數组、月數组等等
  getSecondArr(ruleArr[0])
  getMinArr(ruleArr[1])
  getHourArr(ruleArr[2])
  getDayArr(ruleArr[3])
  getMonthArr(ruleArr[4])
  getWeekArr(ruleArr[5])
  getYearArr(ruleArr[6], nYear)
  // 將獲取到的數组赋值-方便使用
  let sDate = dateArr[0]
  let mDate = dateArr[1]
  let hDate = dateArr[2]
  let DDate = dateArr[3]
  let MDate = dateArr[4]
  let YDate = dateArr[5]
  // 獲取當前時間在數组中的索引
  let sIdx = getIndex(sDate, nSecond)
  let mIdx = getIndex(mDate, nMin)
  let hIdx = getIndex(hDate, nHour)
  let DIdx = getIndex(DDate, nDay)
  let MIdx = getIndex(MDate, nMonth)
  let YIdx = getIndex(YDate, nYear)
  // 重置月日時分秒的函數(後面用的比较多)
  const resetSecond = function () {
    sIdx = 0
    nSecond = sDate[sIdx]
  }
  const resetMin = function () {
    mIdx = 0
    nMin = mDate[mIdx]
    resetSecond()
  }
  const resetHour = function () {
    hIdx = 0
    nHour = hDate[hIdx]
    resetMin()
  }
  const resetDay = function () {
    DIdx = 0
    nDay = DDate[DIdx]
    resetHour()
  }
  const resetMonth = function () {
    MIdx = 0
    nMonth = MDate[MIdx]
    resetDay()
  }
  // 如果當前年份不為數组中當前值
  if (nYear !== YDate[YIdx]) {
    resetMonth()
  }
  // 如果當前月份不為數组中當前值
  if (nMonth !== MDate[MIdx]) {
    resetDay()
  }
  // 如果當前“日”不為數组中當前值
  if (nDay !== DDate[DIdx]) {
    resetHour()
  }
  // 如果當前“時”不為數组中當前值
  if (nHour !== hDate[hIdx]) {
    resetMin()
  }
  // 如果當前“分”不為數组中當前值
  if (nMin !== mDate[mIdx]) {
    resetSecond()
  }

  // 循環年份數组
  goYear: for (let Yi = YIdx; Yi < YDate.length; Yi++) {
    let YY = YDate[Yi]
    // 如果到達最大值時
    if (nMonth > MDate[MDate.length - 1]) {
      resetMonth()
      continue
    }
    // 循環月份數组
    goMonth: for (let Mi = MIdx; Mi < MDate.length; Mi++) {
      // 赋值、方便後面運算
      let MM = MDate[Mi]
      MM = MM < 10 ? '0' + MM : MM
      // 如果到達最大值時
      if (nDay > DDate[DDate.length - 1]) {
        resetDay()
        if (Mi == MDate.length - 1) {
          resetMonth()
          continue goYear
        }
        continue
      }
      // 循環日期數组
      goDay: for (let Di = DIdx; Di < DDate.length; Di++) {
        // 赋值、方便後面運算
        let DD = DDate[Di]
        let thisDD = DD < 10 ? '0' + DD : DD

        // 如果到達最大值時
        if (nHour > hDate[hDate.length - 1]) {
          resetHour()
          if (Di == DDate.length - 1) {
            resetDay()
            if (Mi == MDate.length - 1) {
              resetMonth()
              continue goYear
            }
            continue goMonth
          }
          continue
        }

        // 判断日期的合法性，不合法的話也是跳出當前循環
        if (
          checkDate(YY + '-' + MM + '-' + thisDD + ' 00:00:00') !== true &&
          dayRule !== 'workDay' &&
          dayRule !== 'lastWeek' &&
          dayRule !== 'lastDay'
        ) {
          resetDay()
          continue goMonth
        }
        // 如果日期规则中有值時
        if (dayRule == 'lastDay') {
          // 如果不是合法日期则需要將前將日期調到合法日期即月末最後一天

          if (checkDate(YY + '-' + MM + '-' + thisDD + ' 00:00:00') !== true) {
            while (DD > 0 && checkDate(YY + '-' + MM + '-' + thisDD + ' 00:00:00') !== true) {
              DD--

              thisDD = DD < 10 ? '0' + DD : DD
            }
          }
        } else if (dayRule == 'workDay') {
          // 校驗並調整如果是2月30號這种日期传進来時需調整至正常月底
          if (checkDate(YY + '-' + MM + '-' + thisDD + ' 00:00:00') !== true) {
            while (DD > 0 && checkDate(YY + '-' + MM + '-' + thisDD + ' 00:00:00') !== true) {
              DD--
              thisDD = DD < 10 ? '0' + DD : DD
            }
          }
          // 獲取達到條件的日期是星期X
          let thisWeek = formatDate(new Date(YY + '-' + MM + '-' + thisDD + ' 00:00:00'), 'week')
          // 當星期日時
          if (thisWeek == 1) {
            // 先找下一个日，並判断是否為月底
            DD++
            thisDD = DD < 10 ? '0' + DD : DD
            // 判断下一日已经不是合法日期
            if (checkDate(YY + '-' + MM + '-' + thisDD + ' 00:00:00') !== true) {
              DD -= 3
            }
          } else if (thisWeek == 7) {
            // 當星期6時只需判断不是1號就可進行操作
            if (dayRuleSup !== 1) {
              DD--
            } else {
              DD += 2
            }
          }
        } else if (dayRule == 'weekDay') {
          // 如果指定了是星期幾
          // 獲取當前日期是屬于星期幾
          let thisWeek = formatDate(new Date(YY + '-' + MM + '-' + DD + ' 00:00:00'), 'week')
          // 校驗當前星期是否在星期池（dayRuleSup）中
          if (dayRuleSup.indexOf(thisWeek) < 0) {
            // 如果到達最大值時
            if (Di == DDate.length - 1) {
              resetDay()
              if (Mi == MDate.length - 1) {
                resetMonth()
                continue goYear
              }
              continue goMonth
            }
            continue
          }
        } else if (dayRule == 'assWeek') {
          // 如果指定了是第幾周的星期幾
          // 獲取每月1號是屬于星期幾
          let thisWeek = formatDate(new Date(YY + '-' + MM + '-' + DD + ' 00:00:00'), 'week')
          if (dayRuleSup[1] >= thisWeek) {
            DD = (dayRuleSup[0] - 1) * 7 + dayRuleSup[1] - thisWeek + 1
          } else {
            DD = dayRuleSup[0] * 7 + dayRuleSup[1] - thisWeek + 1
          }
        } else if (dayRule == 'lastWeek') {
          // 如果指定了每月最後一个星期幾
          // 校驗並調整如果是2月30號這种日期传進来時需調整至正常月底
          if (checkDate(YY + '-' + MM + '-' + thisDD + ' 00:00:00') !== true) {
            while (DD > 0 && checkDate(YY + '-' + MM + '-' + thisDD + ' 00:00:00') !== true) {
              DD--
              thisDD = DD < 10 ? '0' + DD : DD
            }
          }
          // 獲取月末最後一天是星期幾
          let thisWeek = formatDate(new Date(YY + '-' + MM + '-' + thisDD + ' 00:00:00'), 'week')
          // 找到要求中最近的那个星期幾
          if (dayRuleSup < thisWeek) {
            DD -= thisWeek - dayRuleSup
          } else if (dayRuleSup > thisWeek) {
            DD -= 7 - (dayRuleSup - thisWeek)
          }
        }
        // 判断時間值是否小于10置換成“05”這种格式
        DD = DD < 10 ? '0' + DD : DD

        // 循環“時”數组
        goHour: for (let hi = hIdx; hi < hDate.length; hi++) {
          let hh = hDate[hi] < 10 ? '0' + hDate[hi] : hDate[hi]

          // 如果到達最大值時
          if (nMin > mDate[mDate.length - 1]) {
            resetMin()
            if (hi == hDate.length - 1) {
              resetHour()
              if (Di == DDate.length - 1) {
                resetDay()
                if (Mi == MDate.length - 1) {
                  resetMonth()
                  continue goYear
                }
                continue goMonth
              }
              continue goDay
            }
            continue
          }
          // 循環"分"數组
          goMin: for (let mi = mIdx; mi < mDate.length; mi++) {
            let mm = mDate[mi] < 10 ? '0' + mDate[mi] : mDate[mi]

            // 如果到達最大值時
            if (nSecond > sDate[sDate.length - 1]) {
              resetSecond()
              if (mi == mDate.length - 1) {
                resetMin()
                if (hi == hDate.length - 1) {
                  resetHour()
                  if (Di == DDate.length - 1) {
                    resetDay()
                    if (Mi == MDate.length - 1) {
                      resetMonth()
                      continue goYear
                    }
                    continue goMonth
                  }
                  continue goDay
                }
                continue goHour
              }
              continue
            }
            // 循環"秒"數组
            goSecond: for (let si = sIdx; si <= sDate.length - 1; si++) {
              let ss = sDate[si] < 10 ? '0' + sDate[si] : sDate[si]
              // 添加當前時間（時間合法性在日期循環時已经判断）
              if (MM !== '00' && DD !== '00') {
                resultArr.push(YY + '-' + MM + '-' + DD + ' ' + hh + ':' + mm + ':' + ss)
                nums++
              }
              // 如果條數满了就退出循環
              if (nums == 5) break goYear
              // 如果到達最大值時
              if (si == sDate.length - 1) {
                resetSecond()
                if (mi == mDate.length - 1) {
                  resetMin()
                  if (hi == hDate.length - 1) {
                    resetHour()
                    if (Di == DDate.length - 1) {
                      resetDay()
                      if (Mi == MDate.length - 1) {
                        resetMonth()
                        continue goYear
                      }
                      continue goMonth
                    }
                    continue goDay
                  }
                  continue goHour
                }
                continue goMin
              }
            } //goSecond
          } //goMin
        } //goHour
      } //goDay
    } //goMonth
  }
  // 判断100年内的结果條數
  if (resultArr.length == 0) {
    resultList = ['沒有達到條件的結果！']
  } else {
    resultList = resultArr
    if (resultArr.length !== 5) {
      resultList.push('最近100年内只有上面' + resultArr.length + '條结果！')
    }
  }
  // 計算完成-顯示结果
  isShow = true
}
// 用于計算某位數字在數组中的索引
const getIndex = (arr, value) => {
  if (value <= arr[0] || value > arr[arr.length - 1]) {
    return 0
  } else {
    for (let i = 0; i < arr.length - 1; i++) {
      if (value > arr[i] && value <= arr[i + 1]) {
        return i + 1
      }
    }
  }
}
// 獲取"年"數组
const getYearArr = (rule, year) => {
  dateArr[5] = getOrderArr(year, year + 100)
  if (rule !== undefined) {
    if (rule.indexOf('-') >= 0) {
      dateArr[5] = getCycleArr(rule, year + 100, false)
    } else if (rule.indexOf('/') >= 0) {
      dateArr[5] = getAverageArr(rule, year + 100)
    } else if (rule !== '*') {
      dateArr[5] = getAssignArr(rule)
    }
  }
}
// 獲取"月"數组
const getMonthArr = (rule) => {
  dateArr[4] = getOrderArr(1, 12)
  if (rule.indexOf('-') >= 0) {
    dateArr[4] = getCycleArr(rule, 12, false)
  } else if (rule.indexOf('/') >= 0) {
    dateArr[4] = getAverageArr(rule, 12)
  } else if (rule !== '*') {
    dateArr[4] = getAssignArr(rule)
  }
}
// 獲取"日"數组-主要為日期规则
const getWeekArr = (rule) => {
  // 只有當日期规则的两个值均為“”時则表達日期是有選項的
  if (dayRule == '' && dayRuleSup == '') {
    if (rule.indexOf('-') >= 0) {
      dayRule = 'weekDay'
      dayRuleSup = getCycleArr(rule, 7, false)
    } else if (rule.indexOf('#') >= 0) {
      dayRule = 'assWeek'
      let matchRule = rule.match(/[0-9]{1}/g)
      dayRuleSup = [Number(matchRule[1]), Number(matchRule[0])]
      dateArr[3] = [1]
      if (dayRuleSup[1] == 7) {
        dayRuleSup[1] = 0
      }
    } else if (rule.indexOf('L') >= 0) {
      dayRule = 'lastWeek'
      dayRuleSup = Number(rule.match(/[0-9]{1,2}/g)[0])
      dateArr[3] = [31]
      if (dayRuleSup == 7) {
        dayRuleSup = 0
      }
    } else if (rule !== '*' && rule !== '?') {
      dayRule = 'weekDay'
      dayRuleSup = getAssignArr(rule)
    }
  }
}
// 獲取"日"數组-少量為日期规则
const getDayArr = (rule) => {
  dateArr[3] = getOrderArr(1, 31)
  dayRule = ''
  dayRuleSup = ''
  if (rule.indexOf('-') >= 0) {
    dateArr[3] = getCycleArr(rule, 31, false)
    dayRuleSup = 'null'
  } else if (rule.indexOf('/') >= 0) {
    dateArr[3] = getAverageArr(rule, 31)
    dayRuleSup = 'null'
  } else if (rule.indexOf('W') >= 0) {
    dayRule = 'workDay'
    dayRuleSup = Number(rule.match(/[0-9]{1,2}/g)[0])
    dateArr[3] = [dayRuleSup]
  } else if (rule.indexOf('L') >= 0) {
    dayRule = 'lastDay'
    dayRuleSup = 'null'
    dateArr[3] = [31]
  } else if (rule !== '*' && rule !== '?') {
    dateArr[3] = getAssignArr(rule)
    dayRuleSup = 'null'
  } else if (rule == '*') {
    dayRuleSup = 'null'
  }
}
// 獲取"時"數组
const getHourArr = (rule) => {
  dateArr[2] = getOrderArr(0, 23)
  if (rule.indexOf('-') >= 0) {
    dateArr[2] = getCycleArr(rule, 24, true)
  } else if (rule.indexOf('/') >= 0) {
    dateArr[2] = getAverageArr(rule, 23)
  } else if (rule !== '*') {
    dateArr[2] = getAssignArr(rule)
  }
}
// 獲取"分"數组
const getMinArr = (rule) => {
  dateArr[1] = getOrderArr(0, 59)
  if (rule.indexOf('-') >= 0) {
    dateArr[1] = getCycleArr(rule, 60, true)
  } else if (rule.indexOf('/') >= 0) {
    dateArr[1] = getAverageArr(rule, 59)
  } else if (rule !== '*') {
    dateArr[1] = getAssignArr(rule)
  }
}
// 獲取"秒"數组
const getSecondArr = (rule) => {
  dateArr[0] = getOrderArr(0, 59)
  if (rule.indexOf('-') >= 0) {
    dateArr[0] = getCycleArr(rule, 60, true)
  } else if (rule.indexOf('/') >= 0) {
    dateArr[0] = getAverageArr(rule, 59)
  } else if (rule !== '*') {
    dateArr[0] = getAssignArr(rule)
  }
}
// 根據传進来的min-max返回一个順序的數组
const getOrderArr = (min, max) => {
  let arr = []
  for (let i = min; i <= max; i++) {
    arr.push(i)
  }
  return arr
}
// 根據规则中指定的零散值返回一个數组
const getAssignArr = (rule) => {
  let arr = []
  let assiginArr = rule.split(',')
  for (let i = 0; i < assiginArr.length; i++) {
    arr[i] = Number(assiginArr[i])
  }
  arr.sort(compare)
  return arr
}
// 根據一定算術规则計算返回一个數组
const getAverageArr = (rule, limit) => {
  let arr = []
  let agArr = rule.split('/')
  let min = Number(agArr[0])
  let step = Number(agArr[1])
  while (min <= limit) {
    arr.push(min)
    min += step
  }
  return arr
}
// 根據规则返回一个具有周期性的數组
const getCycleArr = (rule, limit, status) => {
  // status--表示是否从0開始（则从1開始）
  let arr = []
  let cycleArr = rule.split('-')
  let min = Number(cycleArr[0])
  let max = Number(cycleArr[1])
  if (min > max) {
    max += limit
  }
  for (let i = min; i <= max; i++) {
    let add = 0
    if (status == false && i % limit == 0) {
      add = limit
    }
    arr.push(Math.round((i % limit) + add))
  }
  arr.sort(compare)
  return arr
}
// 比较數字大小（用于Array.sort）
const compare = (value1, value2) => {
  if (value2 - value1 > 0) {
    return -1
  } else {
    return 1
  }
}
// 格式化日期格式如：2017-9-19 18:04:33
const formatDate = (value, type) => {
  // 計算日期相关值
  let time = typeof value == 'number' ? new Date(value) : value
  let Y = time.getFullYear()
  let M = time.getMonth() + 1
  let D = time.getDate()
  let h = time.getHours()
  let m = time.getMinutes()
  let s = time.getSeconds()
  let week = time.getDay()
  // 如果传遞了type的話
  if (type == undefined) {
    return (
      Y +
      '-' +
      (M < 10 ? '0' + M : M) +
      '-' +
      (D < 10 ? '0' + D : D) +
      ' ' +
      (h < 10 ? '0' + h : h) +
      ':' +
      (m < 10 ? '0' + m : m) +
      ':' +
      (s < 10 ? '0' + s : s)
    )
  } else if (type == 'week') {
    // 在quartz中 1為星期日
    return week + 1
  }
}
// 檢查日期是否存在
const checkDate = (value) => {
  let time = new Date(value)
  let format = formatDate(time)
  return value === format
}

// 執行
expressionChange(props.expression)
</script>

<template>
  <ol class="text-center">
    <li v-for="(item, index) in resultList" :key="index" class="leading-9"> {{ item }}</li>
  </ol>
</template>

<style lang="scss" scoped></style>
