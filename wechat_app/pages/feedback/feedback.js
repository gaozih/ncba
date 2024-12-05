const { feedback } = require('../../utils/request.js');

Page({
  data: {
    content: '',
    isSubmitting: false
  },

  handleInput(e) {
    this.setData({
      content: e.detail.value
    });
  },

  async handleSubmit() {
    if (!this.data.content.trim()) {
      wx.showToast({
        title: '请输入反馈内容',
        icon: 'none'
      });
      return;
    }

    try {
      this.setData({ isSubmitting: true });
      await feedback.submit({
        content: this.data.content
      });

      wx.showModal({
        title: '提交成功',
        content: '感谢您的反馈',
        showCancel: false,
        success: () => {
          wx.navigateBack();
        }
      });
    } catch (error) {
      wx.showToast({
        title: '提交失败，请重试',
        icon: 'none'
      });
    } finally {
      this.setData({ isSubmitting: false });
    }
  },

  handleCancel() {
    wx.navigateBack();
  }
}); 