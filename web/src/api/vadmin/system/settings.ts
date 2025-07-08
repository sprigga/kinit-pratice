import request from '@/config/axios'

export const getSystemSettingsTabsApi = (data: any): Promise<IResponse> => {
  return request.post({ url: '/vadmin/system/settings/tabs', data })
}

export const getSystemSettingsApi = (params: any): Promise<IResponse> => {
  return request.get({ url: '/vadmin/system/settings/tabs/values', params })
}

export const putSystemSettingsApi = (data: any): Promise<IResponse> => {
  return request.put({ url: '/vadmin/system/settings/tabs/values', data })
}

// 獲取系统基础配置，每次進入系统時使用
export const getSystemBaseConfigApi = (): Promise<IResponse> => {
  return request.get({ url: '/vadmin/system/settings/base/config' })
}

// 獲取系统隱私協議
export const getSystemPrivacyApi = (): Promise<IResponse> => {
  return request.get({ url: '/vadmin/system/settings/privacy' })
}

// 獲取系统用户協議
export const getSystemAgreementApi = (): Promise<IResponse> => {
  return request.get({ url: '/vadmin/system/settings/agreement' })
}
