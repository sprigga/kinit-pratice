import { useI18n } from '@/hooks/web/useI18n'
import { Table, TableExpose, TableProps, TableSetProps, TableColumn } from '@/components/Table'
import { ElTable, ElMessageBox, ElMessage } from 'element-plus'
import { ref, watch, unref, nextTick, onMounted } from 'vue'
import { isArray, isEmpty } from '@/utils/is'

const { t } = useI18n()

interface UseTableConfig {
  /**
   * 是否初始化的時候請求一次
   */
  immediate?: boolean
  fetchDataApi: () => Promise<{
    list: any[]
    total?: number
  }>
  fetchDelApi?: (ids: string[] | number[] | number | string) => Promise<boolean>
  fetchExportApi?: (header: Recordable[]) => Promise<IResponse>
}

export const useTable = (config: UseTableConfig) => {
  const { immediate = true } = config

  const loading = ref(false)
  const currentPage = ref(1)
  const pageSize = ref(10)
  const total = ref(0)
  const dataList = ref<any[]>([])

  watch(
    () => currentPage.value,
    () => {
      methods.getList()
    }
  )

  watch(
    () => pageSize.value,
    () => {
      // 當前頁不為1時，修改頁數後會導致多次調用getList方法
      if (unref(currentPage) === 1) {
        methods.getList()
      } else {
        currentPage.value = 1
        methods.getList()
      }
    }
  )

  onMounted(() => {
    if (immediate) {
      methods.getList()
    }
  })

  // Table實例
  const tableRef = ref<typeof Table & TableExpose>()

  // ElTable實例
  const elTableRef = ref<ComponentRef<typeof ElTable>>()

  const register = (ref: typeof Table & TableExpose, elRef: ComponentRef<typeof ElTable>) => {
    tableRef.value = ref
    elTableRef.value = unref(elRef)
  }

  const getTable = async () => {
    await nextTick()
    const table = unref(tableRef)
    if (!table) {
      console.error('The table is not registered. Please use the register method to register')
    }
    return table
  }

  const methods = {
    /**
     * 獲取表單數據
     */
    getList: async () => {
      loading.value = true
      try {
        const res = await config?.fetchDataApi()
        if (res) {
          dataList.value = res.list
          total.value = res.total || 0
        }
      } catch (err) {
        console.log('fetchDataApi error')
      } finally {
        loading.value = false
      }
    },

    /**
     * @description 設置table组件的props
     * @param props table组件的props
     */
    setProps: async (props: TableProps = {}) => {
      const table = await getTable()
      table?.setProps(props)
    },

    /**
     * @description 設置column
     * @param columnProps 需要設置的列
     */
    setColumn: async (columnProps: TableSetProps[]) => {
      const table = await getTable()
      table?.setColumn(columnProps)
    },

    /**
     * @description 新增column
     * @param tableColumn 需要新增數據
     * @param index 在哪裡新增
     */
    addColumn: async (tableColumn: TableColumn, index?: number) => {
      const table = await getTable()
      table?.addColumn(tableColumn, index)
    },

    /**
     * @description 删除column
     * @param field 删除哪个數據
     */
    delColumn: async (field: string) => {
      const table = await getTable()
      table?.delColumn(field)
    },

    /**
     * @description 獲取ElTable组件的實例
     * @returns ElTable instance
     */
    getElTableExpose: async () => {
      await getTable()
      return unref(elTableRef)
    },

    refresh: () => {
      methods.getList()
    },

    // sortableChange: (e: any) => {
    //   console.log('sortableChange', e)
    //   const { oldIndex, newIndex } = e
    //   dataList.value.splice(newIndex, 0, dataList.value.splice(oldIndex, 1)[0])
    //   // to do something
    // }

    // 删除數據
    // 如果存在 ids，则直接使用 ids 中的值進行删除
    // 如果不存在 ids，则判断 multiple 的值来進行删除
    // 如果 multiple 為 true，则说明是多選框，獲取多選框中的數據删除
    // 如果為 false，则说明是點擊按钮，则必須传遞當前選擇行的值
    delList: async (
      multiple: boolean,
      ids: string[] | number[] | number | string = [],
      message = true
    ) => {
      const { fetchDelApi } = config
      if (!fetchDelApi) {
        console.warn('fetchDelApi 方法未定義！')
        return
      }
      await getTable()
      let value: string[] | number[] | number | string = []
      if (isEmpty(ids)) {
        if (multiple) {
          if (unref(elTableRef)?.getSelectionRows().length > 0) {
            value = unref(elTableRef)
              ?.getSelectionRows()
              .map((item) => item.id ?? item.sfaadocno)
          } else {
            ElMessage.warning(t('common.delNoData'))
            return
          }
        } else {
          ElMessage.warning(t('common.delNoData'))
          return
        }
      } else {
        value = ids
      }

      const handleResule = () => {
        ElMessage.success(t('common.delSuccess'))

        const idsLength = isArray(value) ? value.length : 1

        // 計算出临界點
        const current =
          unref(total) % unref(pageSize) === idsLength || unref(pageSize) === 1
            ? unref(currentPage) > 1
              ? unref(currentPage) - 1
              : unref(currentPage)
            : unref(currentPage)

        currentPage.value = current
        methods.getList()
      }

      if (message) {
        ElMessageBox.confirm(t('common.delMessage'), t('common.delWarning'), {
          confirmButtonText: t('common.delOk'),
          cancelButtonText: t('common.delCancel'),
          type: 'warning'
        }).then(async () => {
          const result = await fetchDelApi(value)
          if (result) {
            handleResule()
          }
        })
      } else {
        const result = await fetchDelApi(value)
        if (result) {
          handleResule()
        }
      }
    },

    getSelections: async () => {
      await getTable()
      return (unref(elTableRef)?.getSelectionRows() || []) as any[]
    },

    // 導出筛選列表
    exportQueryList: async (headers?: any[]) => {
      const { fetchExportApi } = config
      if (!fetchExportApi) {
        console.warn('fetchExportApi 方法未定義！')
        return
      }

      if (!headers) {
        const table = await getTable()
        headers = table!
          .getColumn()
          .filter((item) => item.show === true && item.type !== 'selection')
          .map((item) => {
            return { field: item.field, label: item.label }
          })
      }

      try {
        loading.value = true
        const res = await fetchExportApi(headers)
        if (res) {
          const a = document.createElement('a')
          a.style.display = 'none'
          a.href = res.data.url
          a.target = '_blank'
          a.download = res.data.filename
          const event = new MouseEvent('click')
          a.dispatchEvent(event)
        }
      } catch (err) {
        console.log('fetchExportApi error')
      } finally {
        loading.value = false
      }
    }
  }

  return {
    tableRegister: register,
    tableMethods: methods,
    tableState: {
      currentPage,
      pageSize,
      total,
      dataList,
      loading
    }
  }
}
