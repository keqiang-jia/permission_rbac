from flask import Flask, request, redirect
from flask import render_template, session
from decorator import permission_required, login_required, role_required
from extention import migrate
from extention import db
from models import User, Role


class Config:
    # 数据库链接配置参数
    SQLALCHEMY_DATABASE_URI = 'sqlite:///data.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


app = Flask(__name__)
app.secret_key = '123456'
app.config.from_object(Config)

db.init_app(app)

migrate.init_app(app, db)


@app.route('/')
def index():
    return render_template('index.html')


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.json.get('username')
        password = request.json.get('password')
        print(username, password)
        user = User()
        user.username = username
        user.password = password
        db.session.add(user)
        user.role.append(Role.query.get(1))  # 默认给用户添加一个普通用户角色
        db.session.commit()
        return {'status': 'success', 'message': '注册成功,接下来就可以去登录了', 'next': '/login'}
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.json.get('username')
        password = request.json.get('password')
        user = User.query.filter(User.username == username).first()
        # 保存用户id到session中
        session['_user_id'] = user.id
        # 这里需要将角色和权限的关系保存到session中，以便后续判断用户是否有权限
        session['permission'] = ':'.join([permission.code for role in user.role for permission in role.permission])
        return {'status': 'success', 'next': '/home', 'message': '登录账号成功'}
    return render_template('login.html')


@app.route("/logout")
def logout():
    session['_user_id'] = ''
    session['permission'] = ''
    return redirect('/')


@app.route('/home')
@login_required
def home():
    return render_template('home.html')


@app.route('/auth/read')
@login_required
@permission_required('read')
def read():
    return render_template('auth/read.html')


@app.route('/auth/commit')
@login_required
@permission_required('commit')
def commit():
    return render_template('auth/commit.html')


@app.route('/auth/write')
@login_required
@permission_required('write')
def write():
    return render_template('auth/write.html')


@app.route("/admin")
@login_required
@role_required('level3')
# @admin_required
def admin():
    return render_template('admin.html')


# 命令行执行flask create，创建数据库表，并填充数据
@app.cli.command()
def create():
    db.drop_all()
    db.create_all()
    import models

    # 用户表填充数据
    user = models.User()
    user.username = '张三'
    user.password = '123456'
    db.session.add(user)

    # 角色表填充数据
    role1 = models.Role(name='普通用户', code='level1')
    role2 = models.Role(name='会员用户', code='level2')
    role3 = models.Role(name='管理员用户', code='level3')
    db.session.add(role1)
    db.session.add(role2)
    db.session.add(role3)

    # 权限表填充数据
    permission1 = models.Permission(url='/auth/read', code='read')
    permission2 = models.Permission(url='/auth/comment', code='commit')
    permission3 = models.Permission(url='/auth/write', code='write')
    permission4 = models.Permission(url='/admin', code='admin')
    db.session.add(permission1)
    db.session.add(permission2)
    db.session.add(permission3)
    db.session.add(permission4)

    # 角色权限关联表填充数据
    role1.permission.append(permission1)
    role1.permission.append(permission2)

    role2.permission.append(permission1)
    role2.permission.append(permission2)
    role2.permission.append(permission3)

    role3.permission.append(permission4)

    # 用户角色关联表填充数据
    user.role.append(role1)

    print(user)
    print([permission.code for role in user.role for permission in role.permission])
    db.session.commit()
