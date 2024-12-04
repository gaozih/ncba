import config from '../../config/config'

Page({
  data: {
    pdfUrl: '',
    loading: true,
    error: false
  },

  onLoad(options) {
    const { id, filename } = options
    this.loadPdfUrl(id)
  },

  async loadPdfUrl(reportId) {
    try {
      const token = wx.getStorageSync(config.TOKEN_STORAGE_KEY)
      // 获取预览URL
      const res = await wx.request({
        url: config.API_BASE_URL + config.API.REPORT_PREVIEW(reportId),
        method: 'GET',
        header: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (res.statusCode === config.STATUS.SUCCESS) {
        this.setData({
          pdfUrl: res.data.previewUrl,
          loading: false
        })
      } else {
        throw new Error('获取预览链接失败')
      }
    } catch (err) {
      this.setData({
        loading: false,
        error: true
      })
      wx.showToast({
        title: '加载失败',
        icon: 'none'
      })
    }
  }
}) 