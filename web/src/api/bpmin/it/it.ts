import request from '@/config/axios'

/** 获取 資訊需求單 列表 */
export const getBpminItListApi = (params: any): Promise<IResponse> => {
  return request.get({ url: '/bpmin/it/it', params })
}

/** 创建 資訊需求單 */
export const addBpminItApi = (data: any): Promise<IResponse> => {
  return request.post({ url: '/bpmin/it/it', data })
}

/** 删除 資訊需求單 */
export const delBpminItApi = (data: any): Promise<IResponse> => {
  return request.delete({ url: '/bpmin/it/it', data })
}

/** 更新 資訊需求單 */
export const putBpminItApi = (data: any): Promise<IResponse> => {
  return request.put({ url: `/bpmin/it/it/${data.id}`, data })
}

/** 获取单个 資訊需求單 详情 */
export const getBpminItApi = (dataId: number): Promise<IResponse> => {
  return request.get({ url: `/bpmin/it/it/${dataId}` })
}
