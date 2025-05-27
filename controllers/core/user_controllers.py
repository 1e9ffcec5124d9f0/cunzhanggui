from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import Blueprint, request, jsonify
from typing import Optional, List
from core.configs import DEBUG_MODE
import services.core.user_services as user_services
import services.core.permission_services as permission_services
from models.core.user import User

user_blueprint = Blueprint('user', __name__, url_prefix='/api/user')


@user_blueprint.route('/create', methods=['POST'])
@jwt_required()
def create_user():
    """创建用户"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    id_card_number = data.get('id_card_number')
    phone_number = data.get('phone_number')
    real_name = data.get('real_name')
    department_id = data.get('department_id')
    
    current_user_id = get_jwt_identity()
    current_user = User.get_user(current_user_id)
    
    try:
        result = user_services.create_user(
            current_user=current_user,
            username=username,
            password=password,
            id_card_number=id_card_number,
            phone_number=phone_number,
            real_name=real_name,
            department_id=department_id
        )
        return jsonify({"code": 200, "message": result}), 200
    except user_services.UserServiceException as e:
        return jsonify({"code": e.code, "message": e.message}), e.code
    except permission_services.PermissionServiceException as e:
        return jsonify({"code": e.code, "message": e.message}), e.code
    except Exception as e:
        if DEBUG_MODE:
            return jsonify({"code": 500, "message": str(e)}), 500
        else:
            return jsonify({"code": 500, "message": "未知错误导致创建用户失败"}), 500


@user_blueprint.route('/update', methods=['PUT'])
@jwt_required()
def update_user():
    """更新用户"""
    data = request.json
    user_id = data.get('user_id')
    username = data.get('username')
    id_card_number = data.get('id_card_number')
    phone_number = data.get('phone_number')
    real_name = data.get('real_name')
    department_id = data.get('department_id')
    role_ids = data.get('role_ids')
    
    current_user_id = get_jwt_identity()
    current_user = User.get_user(current_user_id)
    
    try:
        result = user_services.update_user(
            current_user=current_user,
            user_id=user_id,
            username=username,
            id_card_number=id_card_number,
            phone_number=phone_number,
            real_name=real_name,
            department_id=department_id,
            role_ids=role_ids
        )
        return jsonify({"code": 200, "message": result}), 200
    except user_services.UserServiceException as e:
        return jsonify({"code": e.code, "message": e.message}), e.code
    except permission_services.PermissionServiceException as e:
        return jsonify({"code": e.code, "message": e.message}), e.code
    except Exception as e:
        if DEBUG_MODE:
            return jsonify({"code": 500, "message": str(e)}), 500
        else:
            return jsonify({"code": 500, "message": "未知错误导致更新用户失败"}), 500


@user_blueprint.route('/delete', methods=['DELETE'])
@jwt_required()
def delete_user():
    """删除用户"""
    data = request.json
    user_id = data.get('user_id')
    
    current_user_id = get_jwt_identity()
    current_user = User.get_user(current_user_id)
    
    try:
        result = user_services.delete_user(current_user=current_user, user_id=user_id)
        return jsonify({"code": 200, "message": result}), 200
    except user_services.UserServiceException as e:
        return jsonify({"code": e.code, "message": e.message}), e.code
    except permission_services.PermissionServiceException as e:
        return jsonify({"code": e.code, "message": e.message}), e.code
    except Exception as e:
        if DEBUG_MODE:
            return jsonify({"code": 500, "message": str(e)}), 500
        else:
            return jsonify({"code": 500, "message": "未知错误导致删除用户失败"}), 500


@user_blueprint.route('/get', methods=['GET'])
@jwt_required()
def get_user():
    """获取用户"""
    user_id = request.args.get('user_id', type=int)
    username = request.args.get('username')
    
    current_user_id = get_jwt_identity()
    current_user = User.get_user(current_user_id)
    
    try:
        result = user_services.get_user(
            current_user=current_user,
            user_id=user_id,
            username=username
        )
        return jsonify({"code": 200, "data": result.model_dump(), "message": "获取用户成功"}), 200
    except user_services.UserServiceException as e:
        return jsonify({"code": e.code, "message": e.message}), e.code
    except permission_services.PermissionServiceException as e:
        return jsonify({"code": e.code, "message": e.message}), e.code
    except Exception as e:
        if DEBUG_MODE:
            return jsonify({"code": 500, "message": str(e)}), 500
        else:
            return jsonify({"code": 500, "message": "未知错误导致获取用户失败"}), 500


@user_blueprint.route('/get_current', methods=['GET'])
@jwt_required()
def get_current_user():
    """获取当前用户信息"""
    current_user_id = get_jwt_identity()
    current_user = User.get_user(current_user_id)
    
    try:
        user = user_services.get_user(current_user=current_user)
        result = user.model_dump()
        result.pop("password_hash")
        return jsonify({"code": 200, "data": result, "message": "获取当前用户信息成功"}), 200
    except user_services.UserServiceException as e:
        return jsonify({"code": e.code, "message": e.message}), e.code
    except permission_services.PermissionServiceException as e:
        return jsonify({"code": e.code, "message": e.message}), e.code
    except Exception as e:
        if DEBUG_MODE:
            return jsonify({"code": 500, "message": str(e)}), 500
        else:
            return jsonify({"code": 500, "message": "未知错误导致获取当前用户信息失败"}), 500


@user_blueprint.route('/list', methods=['GET'])
@jwt_required()
def get_users_by_department():
    """根据部门获取用户列表"""
    department_id = request.args.get('department_id', type=int)
    
    current_user_id = get_jwt_identity()
    current_user = User.get_user(current_user_id)
    
    try:
        result = user_services.get_users_by_department(
            current_user=current_user,
            department_id=department_id
        )
        user_list = [user.model_dump() for user in result]
        return jsonify({"code": 200, "data": user_list, "message": "获取用户列表成功"}), 200
    except user_services.UserServiceException as e:
        return jsonify({"code": e.code, "message": e.message}), e.code
    except permission_services.PermissionServiceException as e:
        return jsonify({"code": e.code, "message": e.message}), e.code
    except Exception as e:
        if DEBUG_MODE:
            return jsonify({"code": 500, "message": str(e)}), 500
        else:
            return jsonify({"code": 500, "message": "未知错误导致获取用户列表失败"}), 500


@user_blueprint.route('/change_password', methods=['PUT'])
@jwt_required()
def change_user_password():
    """修改用户密码"""
    data = request.json
    user_id = data.get('user_id')
    new_password = data.get('new_password')
    
    current_user_id = get_jwt_identity()
    current_user = User.get_user(current_user_id)
    
    try:
        result = user_services.change_user_password(
            current_user=current_user,
            user_id=user_id,
            new_password=new_password
        )
        return jsonify({"code": 200, "message": result}), 200
    except user_services.UserServiceException as e:
        return jsonify({"code": e.code, "message": e.message}), e.code
    except permission_services.PermissionServiceException as e:
        return jsonify({"code": e.code, "message": e.message}), e.code
    except Exception as e:
        if DEBUG_MODE:
            return jsonify({"code": 500, "message": str(e)}), 500
        else:
            return jsonify({"code": 500, "message": "未知错误导致修改密码失败"}), 500


@user_blueprint.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.json
    username = data.get('username')
    if not username:
        return jsonify({"code": 400, "message": "用户名不能为空"}), 400
    password = data.get('password')
    if not password:
        return jsonify({"code": 400, "message": "密码不能为空"}), 400
    current_user = User.get_user(username=username)
    
    try:
        result = user_services.login(current_user=current_user, username=username, password=password)
        return jsonify({"code": 200, "message": "登录成功","data":{"access_token":result}}), 200
    except user_services.UserServiceException as e:
        return jsonify({"code": e.code, "message": e.message}), e.code
    except permission_services.PermissionServiceException as e:
        return jsonify({"code": e.code, "message": e.message}), e.code
    except Exception as e:
        if DEBUG_MODE:
            return jsonify({"code": 500, "message": str(e)}), 500
        else:
            return jsonify({"code": 500, "message": "未知错误导致登录失败"}), 500
