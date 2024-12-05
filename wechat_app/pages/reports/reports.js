const { reports } = require('../../utils/request.js');

Page({
  data: {
    reports: [],
    isLoading: true,
    showProgress: false,
    downloadProgress: 0,
    currentPage: 1,
    hasMore: true
  },

  onLoad() {
    this.loadReports();
  },

  onPullDownRefresh() {
    this.setData({
      currentPage: 1,
      hasMore: true
    }, () => {
      this.loadReports(true);
    });
  },

  onReachBottom() {
    if (this.data.hasMore && !this.data.isLoading) {
      this.loadMore();
    }
  },

  async loadReports(isPullDown = false) {
    try {
      this.setData({ isLoading: true });
      const result = await reports.getList({
        page: 1,
        pageSize: 10
      });

      this.setData({
        reports: result.list,
        hasMore: result.list.length >= 10,
        isLoading: false
      });

      if (isPullDown) {
        wx.stopPullDownRefresh();
      }
    } catch (error) {
      this.setData({ isLoading: false });
      wx.showToast({
        title: '加载失败，请重试',
        icon: 'none'
      });
      if (isPullDown) {
        wx.stopPullDownRefresh();
      }
    }
  },

  async loadMore() {
    try {
      this.setData({ isLoading: true });
      const nextPage = this.data.currentPage + 1;
      const result = await reports.getList({
        page: nextPage,
        pageSize: 10
      });

      this.setData({
        reports: [...this.data.reports, ...result.list],
        currentPage: nextPage,
        hasMore: result.list.length >= 10,
        isLoading: false
      });
    } catch (error) {
      this.setData({ isLoading: false });
      wx.showToast({
        title: '加载失败，请重试',
        icon: 'none'
      });
    }
  },

  async handleDownload(e) {
    const reportId = e.currentTarget.dataset.id;
    try {
      this.setData({
        showProgress: true,
        downloadProgress: 0
      });

      const downloadTask = await reports.download(reportId);
      
      downloadTask.onProgressUpdate((res) => {
        this.setData({
          downloadProgress: res.progress
        });

        if (res.progress === 100) {
          this.setData({ showProgress: false });
          // 打开文件
          wx.openDocument({
            filePath: res.tempFilePath,
            success: function (res) {
              console.log('打开文档成功');
            },
            fail: function(error) {
              wx.showToast({
                title: '打开���件失败',
                icon: 'none'
              });
            }
          });
        }
      });
    } catch (error) {
      this.setData({ showProgress: false });
      wx.showToast({
        title: '下载失败，请重试',
        icon: 'none'
      });
    }
  }
}); 