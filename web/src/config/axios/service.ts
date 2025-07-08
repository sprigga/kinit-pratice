import axios, { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse, AxiosError } from 'axios'
import { useAuthStoreWithOut } from '@/store/modules/auth'
import qs from 'qs'
import { config } from './config'
import { ElMessage } from 'element-plus'
import request from '@/config/axios'

const { result_code, unauthorized_code, request_timeout } = config

// 創建axios實例
const service: AxiosInstance = axios.create({
  baseURL: '/api', // api 的 base_url
  timeout: request_timeout, // 請求超時時間
  headers: {} // 請求头信息
})

// request拦截器
service.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const authStore = useAuthStoreWithOut()
    const token = authStore.getToken
    if (token !== '') {
      ;(config.headers as any)[authStore.getTokenKey ?? 'Authorization'] = token // 让每个請求携带自定義token 請根據實際情況自行修改
    }
    if (
      config.method === 'post' &&
      (config.headers as any)['Content-Type'] === 'application/x-www-form-urlencoded'
    ) {
      config.data = qs.stringify(config.data)
    }
    // post put 参數處理
    if (
      (config.method === 'post' || config.method === 'put') &&
      (config.headers as any)['Content-Type'] === 'application/json'
    ) {
      for (const key in config.data) {
        // 参數處理
        if (config.data[key] === '') {
          config.data[key] = null
        }
      }
    }
    // get参數編碼
    if (config.method === 'get' && config.params) {
      let url = config.url as string
      url += '?'
      const keys = Object.keys(config.params)
      for (const key of keys) {
        if (
          // 禁止提交的get参數類型
          config.params[key] !== void 0 &&
          config.params[key] !== null &&
          config.params[key] !== ''
        ) {
          url += `${key}=${encodeURIComponent(config.params[key])}&`
        }
      }
      url = url.substring(0, url.length - 1)
      config.params = {}
      config.url = url
    }
    return config
  },
  (error: AxiosError) => {
    // Do something with request error
    console.log('請求報錯', error) // for debug
    Promise.reject(error)
  }
)

// response 拦截器
service.interceptors.response.use(
  (response: AxiosResponse<any>) => {
    // 這个狀態碼是和後端约定好的
    const code = response.data.code || unauthorized_code
    const message = response.data.message || '後端接口無返回内容'
    const refresh = response.headers['if-refresh']

    if (response.config.responseType === 'blob') {
      // 如果是文件流，直接過
      return response
    } else if (code === result_code) {
      if (refresh === '1') {
        // 因token快過期，刷新token
        refreshToken().then((res) => {
          const authStore = useAuthStoreWithOut()
          authStore.setToken(`${res.data.token_type} ${res.data.access_token}`)
          authStore.setRefreshToken(res.data.refresh_token)
        })
      }
      return response.data
    } else if (code === unauthorized_code) {
      // 因token無效，token過期導致
      refreshToken().then((res) => {
        const authStore = useAuthStoreWithOut()
        authStore.setToken(`${res.data.token_type} ${res.data.access_token}`)
        authStore.setRefreshToken(res.data.refresh_token)
        ElMessage.error('操作失敗，請重試')
      })
    } else {
      ElMessage.error(message)
    }
  },
  (error: AxiosError) => {
    console.log('err', error)
    let { message } = error
    const authStore = useAuthStoreWithOut()
    const status = error.response?.status
    switch (status) {
      case 400:
        message = '請求錯誤'
        break
      case 401:
        // 强制要求重新登錄，因帳號已冻结，帳號已過期，手機號碼错误，刷新token無效等問題導致
        authStore.logout()
        message = '認證已失效，請重新登錄'
        break
      case 403:
        // 强制要求重新登錄，因無系统權限，而進入到系统訪問等問題導致
        authStore.logout()
        message = '無權限訪問，請聯絡管理員'
        break
      case 404:
        message = `請求地址出錯: ${error.response?.config.url}`
        break
      case 408:
        message = '請求超時'
        break
      case 500:
        message = '服務器内部錯誤'
        break
      case 501:
        message = '服務未實現'
        break
      case 502:
        message = '網關錯誤'
        break
      case 503:
        message = '服務不可用'
        break
      case 504:
        message = '網關超時'
        break
      case 505:
        message = 'HTTP版本不受支持'
        break
      default:
        break
    }
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

// 刷新Token
const refreshToken = (): Promise<IResponse> => {
  const authStore = useAuthStoreWithOut()
  const data = authStore.getRefreshToken
  return request.post({ url: '/auth/token/refresh', data })
}

export { service }
