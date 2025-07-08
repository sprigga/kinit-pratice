<script setup lang="ts">
import { ElRadioGroup, ElRadio } from 'element-plus'
import { PropType, computed, defineProps, defineEmits } from 'vue'

// 定義 `props`
const props = defineProps({
  modelValue: {
    type: String,
    required: true
  },
  options: {
    type: Array as PropType<{ label: string; value: string }[]>,
    required: true
  },
  size: {
    type: String as PropType<'default' | 'small' | 'large'>,
    default: 'default'
  },
  disabled: {
    type: Boolean,
    default: false
  }
})

// 定義 `emit`
const emit = defineEmits(['update:modelValue'])

// 讓 `v-model` 能夠正確綁定
const selectedValue = computed({
  get: () => props.modelValue,
  set: (value: string) => {
    emit('update:modelValue', value)
  }
})
</script>

<template>
  <ElRadioGroup v-model="selectedValue" :size="size">
    <ElRadio
      v-for="option in options"
      :key="option.value"
      :label="option.value"
      :disabled="disabled"
    >
      {{ option.label }}
    </ElRadio>
  </ElRadioGroup>
</template>
