import request from '@/config/axios'

/** 获取 資訊需求單歷程 列表 */
export const getBpminItDetailListApi = (params: any): Promise<IResponse> => {
  return request.get({ url: '/bpmin/it/detail', params })
}

/** 创建 資訊需求單歷程 */
export const addBpminItDetailApi = (data: any): Promise<IResponse> => {
  return request.post({ url: '/bpmin/it/detail', data })
}

/** 删除 資訊需求單歷程 */
export const delBpminItDetailApi = (data: any): Promise<IResponse> => {
  return request.delete({ url: '/bpmin/it/detail', data })
}

/** 更新 資訊需求單歷程 */
export const putBpminItDetailApi = (data: any): Promise<IResponse> => {
  return request.put({ url: `/bpmin/it/detail/${data.id}`, data })
}

/** 获取单个 資訊需求單歷程 详情 */
export const getBpminItDetailApi = (dataId: number): Promise<IResponse> => {
  return request.get({ url: `/bpmin/it/detail/${dataId}` })
}
