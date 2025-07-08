// src/api/auth/verify.ts
import request from '@/config/axios'

export const verifyAuthApi = (data: {
  username: string
  password: string
}): Promise<IResponse<{ permissions: string[] }>> => {
  return request.post({
    url: '/auth/verify/login', // 使用原本登入 API
    data
  })
}
