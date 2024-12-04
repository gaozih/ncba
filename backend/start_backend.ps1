# 设置编码为UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 颜色函数
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

# 检查虚拟环境是否存在
if (-not (Test-Path "venv")) {
    Write-ColorOutput Green "正在创建虚拟环境..."
    python -m venv venv
}

# 激活虚拟环境
Write-ColorOutput Green "正在激活虚拟环境..."
.\venv\Scripts\Activate.ps1

# 安装依赖
Write-ColorOutput Green "正在检查并安装依赖..."
pip install -r requirements.txt

# 检查数据库是否存在
$dbPath = "reports.db"
if (-not (Test-Path $dbPath)) {
    Write-ColorOutput Yellow "数据库不存在，正在初始化数据库..."
    
    # 创建Python脚本来初始化数据库
    $initScript = @"
from app import db, create_app
from models.admin import Admin
from datetime import datetime

app = create_app()

with app.app_context():
    # 创建所有表
    db.create_all()
    
    # 检查是否已存在超级管理员
    admin = Admin.query.filter_by(username='admin').first()
    if not admin:
        # 创建超级管理员
        admin = Admin(
            username='admin',
            email='admin@example.com',
            is_super_admin=True,
            is_active=True,
            last_login=datetime.utcnow()
        )
        admin.set_password('Admin123!')
        db.session.add(admin)
        db.session.commit()
        print('超级管理员创建成功！')
        print('用户名: admin')
        print('密码: Admin123!')
    else:
        print('超级管理员已存在')
"@

    # 将脚本写入临时文件
    $initScript | Out-File -Encoding UTF8 "init_db.py"
    
    # 运行初始化脚本
    python init_db.py
    
    # 删除临时脚本
    Remove-Item "init_db.py"
}

# 创建日志目录
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs"
}

# 检查上传目录
if (-not (Test-Path "static/reports")) {
    New-Item -ItemType Directory -Path "static/reports" -Force
}

# 启动Flask应用
Write-ColorOutput Green "正在启动Flask应用..."
Write-ColorOutput Cyan "访问地址: http://localhost:5000"
Write-ColorOutput Cyan "管理后台: http://localhost:5000/admin"
Write-ColorOutput Yellow "按Ctrl+C停止服务器"

$env:FLASK_ENV = "development"
flask run --host=0.0.0.0 --port=5000

# 捕获Ctrl+C
try {
    Wait-Event -Timeout ([System.Threading.Timeout]::Infinite)
} finally {
    # 清理操作
    Write-ColorOutput Yellow "正在停止服务器..."
    deactivate
} 