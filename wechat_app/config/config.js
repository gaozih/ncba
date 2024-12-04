const config = {
  // API域名配置
  API_BASE_URL: 'http://your_api_domain',
  
  // API接口路径
  API: {
    LOGIN: '/api/login',
    SEND_CODE: '/api/send_code',
    REPORTS_LIST: '/api/reports',
    REPORT_DOWNLOAD: (id) => `/api/reports/${id}/download`,
    REPORT_PREVIEW: (id) => `/api/reports/${id}/preview`,
  },
  
  // 状态码配置
  STATUS: {
    SUCCESS: 200,
    UNAUTHORIZED: 401,
    FORBIDDEN: 403,
    NOT_FOUND: 404
  },
  
  // 其他配置
  TOKEN_STORAGE_KEY: 'token',
}

export default config 