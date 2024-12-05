const { auth } = require('../../utils/request.js');

Page({
  data: {
    phone: '',
    code: '',
    countdown: 0,
    isSubmitting: false,
    canSendCode: false,
    isFormValid: false
  },

  handlePhoneInput(e) {
    const phone = e.detail.value;
    this.setData({
      phone,
      canSendCode: /^1\d{10}$/.test(phone)
    });
    this.checkFormValid();
  },

  handleCodeInput(e) {
    this.setData({
      code: e.detail.value
    });
    this.checkFormValid();
  },

  checkFormValid() {
    const { phone, code } = this.data;
    this.setData({
      isFormValid: /^1\d{10}$/.test(phone) && /^\d{6}$/.test(code)
    });
  },

  async handleSendCode() {
    if (!this.data.canSendCode) return;

    try {
      await auth.sendVerifyCode(this.data.phone);
      this.startCountdown();
      wx.showToast({
        title: '验证码已发送',
        icon: 'success'
      });
    } catch (error) {
      wx.showToast({
        title: '发送失败，请重试',
        icon: 'none'
      });
    }
  },

  startCountdown() {
    this.setData({ countdown: 60 });
    this.countdownTimer = setInterval(() => {
      if (this.data.countdown <= 1) {
        clearInterval(this.countdownTimer);
      }
      this.setData({
        countdown: this.data.countdown - 1
      });
    }, 1000);
  },

  async handleSubmit() {
    if (!this.data.isFormValid) return;

    try {
      this.setData({ isSubmitting: true });
      await auth.updatePhone({
        phone: this.data.phone,
        code: this.data.code
      });

      wx.showToast({
        title: '修改成功',
        icon: 'success',
        success: () => {
          setTimeout(() => {
            wx.navigateBack();
          }, 1500);
        }
      });
    } catch (error) {
      wx.showToast({
        title: '修改失败，请重试',
        icon: 'none'
      });
    } finally {
      this.setData({ isSubmitting: false });
    }
  },

  onUnload() {
    // 清理定时器
    if (this.countdownTimer) {
      clearInterval(this.countdownTimer);
    }
  }
}); 