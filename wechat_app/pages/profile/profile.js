const app = getApp();

Page({
  data: {
    userInfo: {},
    version: '1.0.0'
  },

  onLoad() {
    this.loadUserInfo();
  },

  onShow() {
    // 每次显示页面时重新加载用户信息，以更新可能发生的变化（如手机号）
    this.loadUserInfo();
  },

  async loadUserInfo() {
    try {
      // 从本地存储或全局状态获取用户信息
      const userInfo = wx.getStorageSync('userInfo') || {};
      this.setData({ userInfo });
    } catch (error) {
      console.error('加载用户信息失败:', error);
    }
  },

  navigateToFeedback() {
    wx.navigateTo({
      url: '/pages/feedback/feedback'
    });
  },

  navigateToPhone() {
    wx.navigateTo({
      url: '/pages/phone/phone'
    });
  },

  navigateToDelete() {
    wx.navigateTo({
      url: '/pages/delete-account/delete-account'
    });
  }
}); 