const BASE_URL = 'your-api-base-url';

const request = (url, options = {}) => {
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${BASE_URL}${url}`,
      ...options,
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data);
        } else {
          reject(res);
        }
      },
      fail: reject
    });
  });
};

const auth = {
  login: (code) => {
    return request('/auth/login', {
      method: 'POST',
      data: { code }
    });
  },
  bindPhone: (phone, code) => {
    return request('/auth/bind-phone', {
      method: 'POST',
      data: { phone, code }
    });
  },
  validateToken: (token) => {
    return request('/auth/validate-token', {
      method: 'POST',
      data: { token }
    });
  },
  sendVerifyCode: (phone) => {
    return request('/auth/send-code', {
      method: 'POST',
      data: { phone }
    });
  },
  updatePhone: (data) => {
    return request('/auth/update-phone', {
      method: 'POST',
      data
    });
  },
  deleteAccount: () => {
    return request('/auth/delete-account', {
      method: 'POST'
    });
  }
};

const reports = {
  getList: () => {
    return request('/reports', {
      method: 'GET'
    });
  },
  download: (reportId) => {
    return new Promise((resolve, reject) => {
      const downloadTask = wx.downloadFile({
        url: `${BASE_URL}/reports/${reportId}/download`,
        success: (res) => {
          if (res.statusCode === 200) {
            resolve(res.tempFilePath);
          } else {
            reject(new Error('下载失败'));
          }
        },
        fail: reject
      });
      resolve(downloadTask);
    });
  }
};

const feedback = {
  submit: (data) => {
    return request('/feedback/submit', {
      method: 'POST',
      data
    });
  }
};

module.exports = {
  auth,
  reports,
  feedback,
  request
}; 