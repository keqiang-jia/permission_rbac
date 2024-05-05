from extention import db


# 用户表
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='用户ID')
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120))
    password = db.Column(db.String(128))

    role = db.relationship('Role', secondary="user_role", backref=db.backref('user'), lazy='dynamic')


# 角色表
class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, comment='角色名称')
    code = db.Column(db.String(64), unique=True, comment='角色标识')

    permission = db.relationship('Permission', secondary="role_permission", backref=db.backref('role'))


# 权限表
class Permission(db.Model):
    __tablename__ = 'permission'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(64), unique=True, comment='权限路径')
    code = db.Column(db.String(64), comment='权限标识')

    parent_id = db.Column(db.Integer, db.ForeignKey("permission.id"), comment='父类编号')
    parent = db.relationship("Permission", remote_side=[id])  # 自关联


# 用户角色关联表
user_role = db.Table(
    "user_role",
    db.Column("id", db.Integer, primary_key=True, autoincrement=True, comment='标识'),
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), comment='用户编号'),
    db.Column("role_id", db.Integer, db.ForeignKey("role.id"), comment='角色编号'),
)

# 角色权限关联表
role_permission = db.Table(
    "role_permission",
    db.Column("id", db.Integer, primary_key=True, autoincrement=True, comment='标识'),
    db.Column("permission_id", db.Integer, db.ForeignKey("permission.id"), comment='用户编号'),
    db.Column("role_id", db.Integer, db.ForeignKey("role.id"), comment='角色编号'),
)
