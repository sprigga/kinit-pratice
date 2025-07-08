import request from '@/config/axios'

/** 获取 業務拜訪回覆紀錄 列表 */
export const getCrmVisitReplyListApi = (params: any): Promise<IResponse> => {
  return request.get({ url: '/crm/visit/reply', params })
}

/** 创建 業務拜訪回覆紀錄 */
export const addCrmVisitReplyApi = (data: any): Promise<IResponse> => {
  return request.post({ url: '/crm/visit/reply', data })
}

/** 删除 業務拜訪回覆紀錄 */
export const delCrmVisitReplyApi = (data: any): Promise<IResponse> => {
  return request.delete({ url: '/crm/visit/reply', data })
}

/** 更新 業務拜訪回覆紀錄 */
export const putCrmVisitReplyApi = (data: any): Promise<IResponse> => {
  return request.put({ url: `/crm/visit/reply/${data.id}`, data })
}

/** 获取单个 業務拜訪回覆紀錄 详情 */
export const getCrmVisitReplyApi = (dataId: number): Promise<IResponse> => {
  return request.get({ url: `crm/visit/reply/${dataId}` })
}
