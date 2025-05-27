from flask import Flask
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
import os

from core.configs import JWT_SECRET_KEY
from sqlmodel import SQLModel
from core.configs import application_sqlmodel_engine
load_dotenv()

from controllers.core.user_controllers import user_blueprint
from controllers.core.crypto_controllers import crypto_blueprint
from controllers.core.department_controllers import department_blueprint
from controllers.core.role_controllers import role_blueprint
app = Flask(__name__)

jwt = JWTManager(app)

app.register_blueprint(user_blueprint)
app.register_blueprint(crypto_blueprint)
app.register_blueprint(department_blueprint)
app.register_blueprint(role_blueprint)


app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
def init_system():
    SQLModel.metadata.create_all(application_sqlmodel_engine)
    from models.core.department import Department
    try:
        Department.get_root_department()
    except:
        Department.create(name="根部门",level=0,parent_id=None,description="根部门",manager_name="",manager_phone="")
    root_department=Department.get_root_department()
    from models.core.role import Role
    from models.core.permission import PermissionManager
    if len(Role.get_roles_by_department_id(root_department.id))==0:
        Role.create(name="超级管理员",description="超级管理员",department_id=root_department.id,permissions=list(PermissionManager.get_all_permissions().keys()))
    else:
        Role.update(Role.get_roles_by_department_id(root_department.id)[0].id,name="超级管理员",description="超级管理员",permissions=list(PermissionManager.get_all_permissions().keys()))
    from models.core.user import User
    try:
        user=User.get_user(username="admin")
    except:
        User.create(username="admin",password="admin",id_card_number="",phone_number="",real_name="",department_id=root_department.id)
        user=User.get_user(username="admin")
    User.update(user.id,role_ids=[Role.get_roles_by_department_id(root_department.id)[0].id])
if __name__ == '__main__':
    
    init_system()
    app.run(host='0.0.0.0', port=5000, debug=False)
