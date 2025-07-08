import request from '@/config/axios'

/** 获取 日報管理 列表 */
export const getCrmVisitRecordListApi = (params: any): Promise<IResponse> => {
  return request.get({ url: '/crm/visit/record', params })
}

/** 创建 日報管理 */
export const addCrmVisitRecordApi = (data: any): Promise<IResponse> => {
  return request.post({ url: '/crm/visit/record', data })
}

/** 删除 日報管理 */
export const delCrmVisitRecordApi = (data: any): Promise<IResponse> => {
  return request.delete({ url: '/crm/visit/record', data })
}

/** 更新 日報管理 */
export const putCrmVisitRecordApi = (data: any): Promise<IResponse> => {
  return request.put({ url: `/crm/visit/record/${data.id}`, data })
}

/** 获取单个 日報管理 详情 */
export const getCrmVisitRecordApi = (dataId: number): Promise<IResponse> => {
  return request.get({ url: `crm/visit/record/${dataId}` })
}
