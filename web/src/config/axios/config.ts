const config: {
  result_code: number | string
  unauthorized_code: number | string
  default_headers: AxiosHeaders
  request_timeout: number
} = {
  /**
   * 接口成功返回狀態碼
   */
  result_code: 200,
  /**
   * 接口TOKEN失效，返回狀態碼
   */
  unauthorized_code: 401,

  /**
   * 接口請求超時時間
   */
  request_timeout: 60000,

  /**
   * 默認接口請求類型
   * 可選值：application/x-www-form-urlencoded multipart/form-data
   */
  default_headers: 'application/json'
}

export { config }
