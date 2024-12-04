import config from '../../config/config'

Page({
  data: {
    reports: [],
    loading: true
  },

  onLoad() {
    this.fetchReports()
  },

  // 获取报告列表
  async fetchReports() {
    try {
      const token = wx.getStorageSync(config.TOKEN_STORAGE_KEY)
      const res = await wx.request({
        url: config.API_BASE_URL + config.API.REPORTS_LIST,
        method: 'GET',
        header: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (res.statusCode === config.STATUS.SUCCESS) {
        this.setData({
          reports: res.data.reports.map(report => ({
            ...report,
            upload_time: this.formatDate(report.upload_time)
          })),
          loading: false
        })
      } else {
        throw new Error('获取报告失败')
      }
    } catch (err) {
      wx.showToast({
        title: '获取报告失败',
        icon: 'none'
      })
      this.setData({ loading: false })
    }
  },

  // 预览报告
  previewReport(e) {
    const { id, filename } = e.currentTarget.dataset
    wx.navigateTo({
      url: `/pages/preview/preview?id=${id}&filename=${filename}`
    })
  },

  // 下载报告
  async downloadReport(e) {
    const { id, filename } = e.currentTarget.dataset
    wx.showLoading({ title: '下载中...' })

    try {
      const token = wx.getStorageSync(config.TOKEN_STORAGE_KEY)
      const res = await wx.downloadFile({
        url: config.API_BASE_URL + config.API.REPORT_DOWNLOAD(id),
        header: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (res.statusCode === config.STATUS.SUCCESS) {
        wx.openDocument({
          filePath: res.tempFilePath,
          success: function (res) {
            console.log('打开文档成功')
          }
        })
      } else {
        throw new Error('下载失败')
      }
    } catch (err) {
      wx.showToast({
        title: '下载失败',
        icon: 'none'
      })
    } finally {
      wx.hideLoading()
    }
  },

  formatDate(dateStr) {
    const date = new Date(dateStr)
    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
  }
}) 