import json
import re
from pathlib import Path

from application.settings import BASE_DIR


class FrontendFileGenerator:
    def __init__(self, model, base_class_name, zh_name, en_name):
        self.model = model  # 这里传递的是模型类对象
        self.base_class_name = base_class_name
        self.zh_name = zh_name
        self.en_name = en_name

    def generate_frontend_files(self):
        """
        自动生成前端 API 调用模板 (Vue3/TypeScript)、
        列表页面 (Members.vue) 以及编辑页面 (components/Write.vue)。
        根据模型名称生成对应的目录结构和文件。
        """
        # 拆分模型名称，例如 'LotteryMembers' -> ['Lottery', 'Members']
        class_model_name = self.model.__name__  # 获取模型类的名称
        model_name_parts = re.findall(r'[A-Z][a-z]*', self.model.__name__)
        folder_name = model_name_parts[0].lower()  # 'lottery'
        model_name = model_name_parts[1].lower()  # 'members'
        
        # 修正這一行，處理不同長度的模型名稱
        if len(model_name_parts) >= 3:
            fun_name = model_name_parts[2].lower()  # 如果有第三部分，使用第三部分
        elif len(model_name_parts) == 2:
            fun_name = model_name_parts[1].lower()  # 如果只有兩部分，使用第二部分
        else:
            fun_name = model_name_parts[0].lower()  # 如果只有一部分，使用第一部分
        

        # 获取上一级目录，即主项目的目录
        main_project_dir = Path(BASE_DIR).parent  # 上一级目录，主项目目录
        base_web_dir = main_project_dir / f"web"  # 例如 'tw_lottery-web'
        print(base_web_dir)
        # 生成目标API目录路径，动态生成 'lottery/members' 路径
        api_dir = base_web_dir / "src" / "api" / folder_name / model_name  # 'lottery/members' 路径
        api_file_path = api_dir / f"{fun_name}.ts"  # 'members.ts' 文件路径

        # 确保目录存在
        api_dir.mkdir(parents=True, exist_ok=True)

        # 生成前端 API 调用模板
        self._generate_api_file(api_file_path, folder_name, model_name + '/' + fun_name)

        # 生成列表页面 (Members.vue)
        list_file_name = f"{fun_name.capitalize()}.vue"  # 'Members.vue' 文件名
        list_api_dir = base_web_dir / "src" / "views" / folder_name.capitalize() / model_name.capitalize()  / fun_name.capitalize()# 路径
        list_api_file_path = list_api_dir / list_file_name  # 'Members.vue' 文件路径
        # 确保目录存在
        list_api_dir.mkdir(parents=True, exist_ok=True)

        # 生成 Vue 文件内容
        self._generate_vue_list_file(list_api_file_path, folder_name, model_name, fun_name)

        # 生成编辑页面 (Write.vue)
        write_file_name = "Write.vue"
        write_api_file_path = base_web_dir / "src" / "views" / folder_name.capitalize() / model_name.capitalize() / fun_name.capitalize() / "components" / write_file_name  # 路径

        # 确保目录存在
        write_api_file_path.parent.mkdir(parents=True, exist_ok=True)

        # 生成编辑页面内容
        self._generate_vue_edit_file(write_api_file_path)

    def _generate_api_file(self, api_file_path, folder_name, model_name):
        """生成前端 API 调用模板"""
        content = f"""import request from '@/config/axios'

/** 获取 {self.zh_name} 列表 */
export const get{self.base_class_name}ListApi = (params: any): Promise<IResponse> => {{
  return request.get({{ url: '/{folder_name}/{model_name}', params }})
}}

/** 创建 {self.zh_name} */
export const add{self.base_class_name}Api = (data: any): Promise<IResponse> => {{
  return request.post({{ url: '/{folder_name}/{model_name}', data }})
}}

/** 删除 {self.zh_name} */
export const del{self.base_class_name}Api = (data: any): Promise<IResponse> => {{
  return request.delete({{ url: '/{folder_name}/{model_name}', data }})
}}

/** 更新 {self.zh_name} */
export const put{self.base_class_name}Api = (data: any): Promise<IResponse> => {{
  return request.put({{ url: `/{folder_name}/{model_name}/${{data.id}}`, data }})
}}

/** 获取单个 {self.zh_name} 详情 */
export const get{self.base_class_name}Api = (dataId: number): Promise<IResponse> => {{
  return request.get({{ url: `/{folder_name}/{model_name}/${{dataId}}` }})
}}
"""
        api_file_path.write_text(content.strip() + "\n", encoding="utf-8")
        print(f"成功生成前端 API 文件: {api_file_path}")

    def _generate_vue_list_file(self, list_api_file_path, folder_name, model_name, fun_name):
        """生成 Vue 列表页面"""
        vue_content = f"""
<script setup lang="tsx">
import {{ reactive, ref, unref }} from 'vue'
import {{
  get{self.base_class_name}ListApi,
  add{self.base_class_name}Api,
  del{self.base_class_name}Api,
  put{self.base_class_name}Api,
  get{self.base_class_name}Api
}} from '@/api/{folder_name}/{model_name}/{fun_name}'

import {{ useTable }} from '@/hooks/web/useTable'
import {{ useI18n }} from '@/hooks/web/useI18n'
import {{ Table, TableColumn }} from '@/components/Table'
import {{ ElRow, ElCol }} from 'element-plus'
import {{ Search }} from '@/components/Search'
import {{ FormSchema }} from '@/components/Form'
import {{ ContentWrap }} from '@/components/ContentWrap'
import Write from './components/Write.vue'
import {{ Dialog }} from '@/components/Dialog'
import {{ useDictStore }} from '@/store/modules/dict'
import {{ DictDetail }} from '@/utils/dict'
import {{ BaseButton }} from '@/components/Button'

defineOptions({{
  name: '{self.model.__name__}'
}})

const {{ t }} = useI18n()

const {{ tableRegister, tableState, tableMethods }} = useTable({{
  fetchDataApi: async () => {{
    const {{ pageSize, currentPage }} = tableState
    const res = await get{self.base_class_name}ListApi({{
      page: unref(currentPage),
      limit: unref(pageSize),
      ...unref(searchParams)
    }})
    return {{
      list: res.data || [],
      total: res.count || 0
    }}
  }},
  fetchDelApi: async (value) => {{
    const res = await del{self.base_class_name}Api(value)
    return res.code === 200
  }}
}})

const {{ dataList, loading, total, pageSize, currentPage }} = tableState
const {{ getList, delList }} = tableMethods

const platformOptions = ref<DictDetail[]>([])

const getOptions = async () => {{
  const dictStore = useDictStore()
  const dictOptions = await dictStore.getDictObj(['sys_vadmin_platform'])
  platformOptions.value = dictOptions.sys_vadmin_platform
}}

getOptions()

const tableColumns = reactive<TableColumn[]>(["""
        # 根据每个字段配置自动生成 Vue 表格列
        for i, column in enumerate(self.model.column_config.keys()):
            config = self.model.column_config[column]
            if config['show_in_list']:
                is_last_column = (i == len(self.model.column_config.keys()) - 1)
                vue_content += f"""
  {{
    field: '{column}',
    label: '{config['label']}',
    width: '150px',
    show: true,
    disabled: true
  }}{',' if not is_last_column else ','}"""
    # 添加操作列
        vue_content += f"""
  {{
    field: 'action',
    label: '操作',
    width: '200px',
    show: true,
    slots: {{
      default: (data: any) => {{
        const row = data.row
        const update = ['{folder_name}.{model_name}.{fun_name}.update']
        const del = ['{folder_name}.{model_name}.{fun_name}.delete']
        return (
          <>
            <BaseButton
              type="primary"
              v-hasPermi={{update}}
              link
              size="small"
              onClick={{() => editAction(row)}}
            >
              編輯
            </BaseButton>
            <BaseButton
              type="danger"
              v-hasPermi={{del}}
              loading={{delLoading.value}}
              link
              size="small"
              onClick={{() => delData(row)}}
            >
              删除
            </BaseButton>
          </>
        )
      }}
    }}
  }}"""
        vue_content += """
])

const searchSchema = reactive<FormSchema[]>(["""
        # 生成搜尋框 (searchSchema)
        search_schema = []
        for column, config in self.model.column_config.items():
            if config['show_in_search']:
                field_type = config.get('field_type', 'input')  # 確保 field_type 有預設值 'input'

                if field_type == 'select':  # 处理下拉选单
                    options = config.get('options', [])
                    formatted_options = ",\n        ".join([
                        f"{{ label: '{opt}', value: '{opt}' }}" if isinstance(opt,
                                                                              str) else f"{{ label: '{opt['label']}', value: '{opt['value']}' }}"
                        for opt in options
                    ])
                    search_schema.append(f"""
  {{
    field: '{column}',
    label: '{config['label']}',
    component: 'Select',
    componentProps: {{
      clearable: true,
      style: {{ width: '214px' }},
      options: [
        {formatted_options}
      ]
    }}
  }}""")
                elif field_type == 'date':  # 日期選擇器
                    search_schema.append(f"""
  {{
    field: '{column}',
    label: '{config['label']}',
    component: 'DatePicker',
    componentProps: {{
      clearable: true,
      style: {{ width: '214px' }}
    }}
  }}""")
            else:  # 默認為 Input
                search_schema.append(f"""
  {{
    field: '{column}',
    label: '{config['label']}',
    component: 'Input',
    componentProps: {{
      clearable: true,
      style: {{ width: '214px' }}
    }}
  }}""")
        vue_content += ",".join(search_schema)
        vue_content += """
])

const searchParams = ref({})
const setSearchParams = (data: any) => {
  currentPage.value = 1
  searchParams.value = data
  getList()
}

const delLoading = ref(false)

const delData = async (row: any) => {
  delLoading.value = true
  await delList(true, [row.id]).finally(() => {
    delLoading.value = false
  })
}

const dialogVisible = ref(false)
const dialogTitle = ref('')

const currentRow = ref()
const actionType = ref('')

const writeRef = ref<ComponentRef<typeof Write>>()

const saveLoading = ref(false)"""
        vue_content += f"""

const editAction = async (row: any) => {{
  const res = await get{self.base_class_name}Api(row.id)
  if (res) {{
    dialogTitle.value = '編輯資料'
    actionType.value = 'edit'
    currentRow.value = res.data
    dialogVisible.value = true
  }}
}}

const addAction = () => {{
  dialogTitle.value = '新增資料'
  actionType.value = 'add'
  currentRow.value = undefined
  dialogVisible.value = true
}}

const add = ['{folder_name}.{model_name}.{fun_name}.create']

const save = async () => {{
  const write = unref(writeRef)
  const formData = await write?.submit()
  if (formData) {{
    saveLoading.value = true
    try {{
      const res = ref({{}})
      if (actionType.value === 'add') {{
        res.value = await add{self.base_class_name}Api(formData)
        if (res.value) {{
          dialogVisible.value = false
          getList()
        }}
      }} else if (actionType.value === 'edit') {{
        res.value = await put{self.base_class_name}Api(formData)
        if (res.value) {{
          dialogVisible.value = false
          getList()
        }}
      }}
    }} finally {{
      saveLoading.value = false
    }}
  }}
}}
</script>

<template>
  <ContentWrap>
    <Search :schema="searchSchema" @reset="setSearchParams" @search="setSearchParams" />
    <Table
      v-model:current-page="currentPage"
      v-model:page-size="pageSize"
      showAction
      :columns="tableColumns"
      default-expand-all
      node-key="id"
      :data="dataList"
      :loading="loading"
      :pagination="{{
        total
      }}"
      @register="tableRegister"
      @refresh="getList"
    >
      <template #toolbar>
        <ElRow :gutter="10">
          <ElCol :span="1.5">
            <BaseButton type="primary" v-hasPermi="{{ add }}" @click="addAction">新增資料</BaseButton>
          </ElCol>
        </ElRow>
      </template>
    </Table>
  </ContentWrap>
  <Dialog v-model="dialogVisible" :title="dialogTitle" :height="650">
    <Write ref="writeRef" :current-row="currentRow" />

    <template #footer>
      <BaseButton type="primary" :loading="saveLoading" @click="save">
        {{{{ t('exampleDemo.save') }}}}
      </BaseButton>
      <BaseButton @click="dialogVisible = false">{{{{ t('dialogDemo.close') }}}}</BaseButton>
    </template>
  </Dialog>
</template>
    """
        list_api_file_path.write_text(vue_content.strip()+'\n', encoding="utf-8")
        print(f"成功生成 Vue 列表页面: {list_api_file_path}")

    def _generate_vue_edit_file(self, write_api_file_path):
        """生成 Vue 编辑页面"""
        form_schema_list = []  # 存放所有字段的 Schema 配置
        # 生成路徑加工
        # 根據字段配置生成
        for column, config in self.model.column_config.items():
            field_type = config.get("field_type", "input")  # 預設 Input
            field_label = config["label"]

            # 下拉選單處理
            if field_type == "select":
                options = config.get("options", [])
                formatted_options = [
                    {"label": str(opt) if isinstance(opt, str) else opt['label'],
                     "value": str(opt) if isinstance(opt, str) else opt['value']}
                    for opt in options
                ]
                component_props = {
                    "clearable": True,
                    "options": formatted_options
                }
                component = "Select"

            # 日期選擇器處理
            elif field_type == "date":
                component_props = {
                    "type": "date",
                    "placeholder": "请选择日期",
                    "style": {"width": "100%"}
                }
                component = "DatePicker"

            # 默認 Input 處理
            else:
                component_props = {"style": {"width": "100%"}}
                component = "Input"

            # 構建每個字段的配置
            field_config = {
                "field": column,
                "label": field_label,
                "colProps": {"span": 12},
                "component": component,
                "componentProps": component_props
            }

            form_schema_list.append(field_config)

        # 格式化 formSchema JSON
        form_schema_json = json.dumps(form_schema_list, indent=2, ensure_ascii=False).replace('"', "'")
        form_schema_json = re.sub(r"'(\w+)':", r"\1:", form_schema_json)

        # 生成 rules 部分，確保格式正確並換行，最後一行不帶逗號
        required_fields = [
            f"  {column}: [required()]"
            for column, config in self.model.column_config.items()
            if config.get("required", False)
        ]
        rules_formatted = ",\n".join(required_fields)

        # 組裝最終的 Vue 內容
        vue_content_write = f"""
<script setup lang="tsx">
import {{ Form, FormSchema }} from '@/components/Form'
import {{ useForm }} from '@/hooks/web/useForm'
import {{ PropType, reactive, watch }} from 'vue'
import {{ useValidator }} from '@/hooks/web/useValidator'

const {{ required }} = useValidator()

const props = defineProps({{
  currentRow: {{
    type: Object as PropType<any>,
    default: () => null
  }}
}})

const formSchema = reactive<FormSchema[]>({form_schema_json})

const rules = reactive({{
{rules_formatted}
}})

const {{ formRegister, formMethods }} = useForm()
const {{ setValues, getFormData, getElFormExpose }} = formMethods

const submit = async () => {{
  const elForm = await getElFormExpose()
  const valid = await elForm?.validate()
  if (valid) {{
    const formData = await getFormData()
    return formData
  }}
}}

watch(
  () => props.currentRow,
  (currentRow) => {{
    if (!currentRow) return
    setValues(currentRow)
  }},
  {{
    deep: true,
    immediate: true
  }}
)

defineExpose({{
  submit
}})
</script>

<template>
  <Form :rules="rules" @register="formRegister" :schema="formSchema" />
</template>
    """

        write_api_file_path.write_text(vue_content_write.strip() + '\n', encoding="utf-8")
        print(f"成功生成 Vue 编辑页面: {write_api_file_path}")


if __name__ == '__main__':
    pass