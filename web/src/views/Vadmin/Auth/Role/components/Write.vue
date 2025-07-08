<script setup lang="tsx">
import { Form, FormSchema } from '@/components/Form'
import { useForm } from '@/hooks/web/useForm'
import { PropType, reactive, watch } from 'vue'
import { useValidator } from '@/hooks/web/useValidator'
// import { ElTree } from 'element-plus'
// import { getMenuRoleTreeOptionsApi } from '@/api/vadmin/auth/menu'
// import { eachTree } from '@/utils/tree'

const { required } = useValidator()

const props = defineProps({
  currentRow: {
    type: Object as PropType<any>,
    default: () => null
  }
})

// let treeData = ref([] as any[])
// const treeRef = ref<InstanceType<typeof ElTree>>()

// const getMenuRoleTreeOptions = async () => {
//   const res = await getMenuRoleTreeOptionsApi()
//   if (res) {
//     treeData.value = res.data
//     await nextTick()
//     if (props.currentRow) {
//       const menu_ids: number[] = props.currentRow.menus.map((item) => item.id)
//       const checked: number[] = []
//       // 遞歸按順序添加選中的選單項，用于處理半選狀態的選單項
//       eachTree(res.data, (v) => {
//         if (menu_ids.includes(v.value)) {
//           checked.push(v.value)
//         }
//       })
//       for (const item of checked) {
//         unref(treeRef)?.setChecked(item, true, false)
//       }
//     }
//   }
// }

// const defaultProps = {
//   children: 'children',
//   label: 'label'
// }

// let selectAll = ref(false)
// let defaultExpandAll = ref(true)
// let checkStrictly = ref(true)

// 獲取所有節點的key
const getTreeNodeKeys = (nodes: Recordable[]): number[] => {
  let keys = [] as number[]
  for (let i = 0; i < nodes.length; i++) {
    keys.push(nodes[i].value)
    if (nodes[i].children && nodes[i].children.length > 0) {
      keys = keys.concat(getTreeNodeKeys(nodes[i].children))
    }
  }
  return keys
}

// // 展開/折叠
// const handleCheckedTreeExpand = (value: boolean) => {
//   defaultExpandAll.value = value
//   for (let i = 0; i < treeData.value.length; i++) {
//     treeRef.value!.store.nodesMap[treeData.value[i].value].expanded = value
//   }
// }

// //全選/全不選
// const handleCheckedTreeNodeAll = (value: boolean) => {
//   selectAll.value = value
//   treeRef.value!.setCheckedKeys(value ? getTreeNodeKeys(treeData.value) : [])
// }

const formSchema = reactive<FormSchema[]>([
  {
    field: 'name',
    label: '角色名稱',
    colProps: {
      span: 12
    },
    component: 'Input'
  },
  {
    field: 'role_key',
    label: '權限字符',
    colProps: {
      span: 12
    },
    component: 'Input'
  },
  {
    field: 'disabled',
    label: '角色狀態',
    colProps: {
      span: 12
    },
    component: 'RadioGroup',
    componentProps: {
      style: {
        width: '100%'
      },
      options: [
        {
          label: '正常',
          value: false
        },
        {
          label: '禁用',
          value: true
        }
      ]
    },
    value: false
  },
  {
    field: 'is_admin',
    label: '最高權限',
    colProps: {
      span: 12
    },
    component: 'RadioGroup',
    componentProps: {
      style: {
        width: '100%'
      },
      options: [
        {
          label: '使用',
          value: true
        },
        {
          label: '不使用',
          value: false
        }
      ]
    },
    value: false
  },
  {
    field: 'order',
    label: '顯示排序',
    colProps: {
      span: 12
    },
    component: 'InputNumber',
    componentProps: {
      style: {
        width: '100%'
      }
    }
  },
  {
    field: 'desc',
    label: '角色描述',
    colProps: {
      span: 24
    },
    component: 'Input',
    componentProps: {
      rows: 4,
      type: 'textarea',
      style: {
        width: '600px'
      }
    }
  }
  // {
  //   field: 'menu_ids',
  //   label: '選單權限',
  //   colProps: {
  //     span: 24
  //   },
  //   formItemProps: {
  //     slots: {
  //       default: () => {
  //         return (
  //           <>
  //             <div>
  //               <div>
  //                 <ElCheckbox
  //                   modelValue={defaultExpandAll.value}
  //                   onChange={handleCheckedTreeExpand}
  //                   label="展開/折叠"
  //                   size="large"
  //                 />
  //                 <ElCheckbox
  //                   modelValue={selectAll.value}
  //                   onChange={handleCheckedTreeNodeAll}
  //                   label="全選/全不選"
  //                   size="large"
  //                 />
  //                 <ElCheckbox v-model={checkStrictly.value} label="父子聯動" size="large" />
  //               </div>
  //               <div class="max-h-420px b-1 b-solid b-[#e5e7eb] p-10px overflow-auto">
  //                 <ElTree
  //                   ref={treeRef}
  //                   data={treeData.value}
  //                   show-checkbox
  //                   node-key="value"
  //                   props={defaultProps}
  //                   default-expand-all={defaultExpandAll.value}
  //                   check-strictly={!checkStrictly.value}
  //                 ></ElTree>
  //               </div>
  //             </div>
  //           </>
  //         )
  //       }
  //     }
  //   }
  // }
])

const rules = reactive({
  name: [required()],
  role_key: [required()],
  order: [required()]
})

const { formRegister, formMethods } = useForm()
const { setValues, getFormData, getElFormExpose } = formMethods

const submit = async () => {
  const elForm = await getElFormExpose()
  const valid = await elForm?.validate()
  if (valid) {
    const formData = await getFormData()
    // formData.menu_ids = [
    //   ...(unref(treeRef)?.getCheckedKeys() || []),
    //   ...(unref(treeRef)?.getHalfCheckedKeys() || [])
    // ]
    return formData
  }
}

watch(
  () => props.currentRow,
  (currentRow) => {
    if (!currentRow) return
    setValues(currentRow)
  },
  {
    deep: true,
    immediate: true
  }
)

// getMenuRoleTreeOptions()

defineExpose({
  submit
})
</script>

<template>
  <Form :rules="rules" @register="formRegister" :schema="formSchema" />
</template>
