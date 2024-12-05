const { auth } = require('../../utils/request.js');

Page({
  data: {
    hasUserInfo: false,
    hasPhoneNumber: false,
    showDialog: false,
    dialogMessage: '',
    dialogButtons: [{ text: '确定' }]
  },

  onLoad() {
    // 检查登录状态
    this.checkLoginStatus();
  },

  async checkLoginStatus() {
    try {
      const token = wx.getStorageSync('token');
      if (token) {
        // 如果有token，验证token是否有效
        const isValid = await this.validateToken(token);
        if (isValid) {
          this.navigateToMain();
          return;
        }
      }
      // token无效或不存在，继续登录流程
      this.setData({ hasUserInfo: false, hasPhoneNumber: false });
    } catch (error) {
      console.error('检查登录状态失败:', error);
    }
  },

  async handleGetUserInfo(e) {
    if (e.detail.userInfo) {
      try {
        const { code } = await wx.login();
        const loginResult = await auth.login(code);
        
        if (loginResult.needBindPhone) {
          this.setData({ 
            hasUserInfo: true,
            hasPhoneNumber: false
          });
        } else {
          // 已经绑定过手机号，直接登录成功
          wx.setStorageSync('token', loginResult.token);
          this.navigateToMain();
        }
      } catch (error) {
        this.showError('登录失败，请重试');
      }
    } else {
      this.showError('需要您的授权才能继续使用');
    }
  },

  async handleGetPhoneNumber(e) {
    if (e.detail.errMsg === 'getPhoneNumber:ok') {
      try {
        const result = await auth.bindPhone({
          code: e.detail.code
        });
        
        wx.setStorageSync('token', result.token);
        this.navigateToMain();
      } catch (error) {
        this.showError('手机号绑定失败，请重试');
      }
    } else {
      this.showError('需要绑定手机号才能继续使用');
    }
  },

  async validateToken(token) {
    try {
      // 调用后端验证token的接口
      const result = await auth.validateToken(token);
      return result.isValid;
    } catch (error) {
      return false;
    }
  },

  navigateToMain() {
    wx.switchTab({
      url: '/pages/reports/reports'
    });
  },

  showError(message) {
    this.setData({
      showDialog: true,
      dialogMessage: message
    });
  },

  tapDialogButton() {
    this.setData({
      showDialog: false
    });
  }
}); 