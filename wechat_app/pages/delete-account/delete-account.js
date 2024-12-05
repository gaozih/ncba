const { auth } = require('../../utils/request.js');

Page({
  data: {
    confirmText: '',
    isDeleting: false
  },

  handleInput(e) {
    this.setData({
      confirmText: e.detail.value
    });
  },

  async handleDelete() {
    if (this.data.confirmText !== '注销账号') return;

    try {
      this.setData({ isDeleting: true });

      await wx.showModal({
        title: '最终确认',
        content: '此操作不可撤销，是否确认注销账号？',
        confirmText: '确认注销',
        confirmColor: '#ff4d4f'
      });

      await auth.deleteAccount();

      // 清除本地存储的用户信息和token
      wx.clearStorageSync();

      wx.showToast({
        title: '账号已注销',
        icon: 'success',
        success: () => {
          // 重定向到登录页
          wx.reLaunch({
            url: '/pages/login/login'
          });
        }
      });
    } catch (error) {
      if (error.errMsg !== 'showModal:cancel') {
        wx.showToast({
          title: '注销失败，请重试',
          icon: 'none'
        });
      }
    } finally {
      this.setData({ isDeleting: false });
    }
  },

  handleCancel() {
    wx.navigateBack();
  }
}); 