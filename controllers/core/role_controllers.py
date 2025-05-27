from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import Blueprint, request, jsonify
from typing import List, Optional
from core.configs import DEBUG_MODE
import services.core.role_services as role_services
import services.core.permission_services as permission_services
from models.core.user import User

role_blueprint = Blueprint('role', __name__, url_prefix='/api/role')


@role_blueprint.route('/create', methods=['POST'])
@jwt_required()
def create_role():
    """创建角色"""
    data = request.json
    name = data.get('name')
    description = data.get('description')
    permissions = data.get('permissions', [])
    department_id = data.get('department_id', None)
    current_user_id = get_jwt_identity()
    current_user = User.get_user(current_user_id)
    
    try:
        result = role_services.create_role(current_user, name, description, permissions, department_id)
        return jsonify({"code": 200, "message": result}), 200
    except role_services.RoleServiceException as e:
        return jsonify({"code": e.code, "message": e.message}), e.code
    except permission_services.PermissionServiceException as e:
        return jsonify({"code": e.code, "message": e.message}), e.code
    except Exception as e:
        if DEBUG_MODE:
            return jsonify({"code": 500, "message": str(e)}), 500
        else:
            return jsonify({"code": 500, "message": "未知错误导致创建角色失败"}), 500


@role_blueprint.route('/update', methods=['PUT'])
@jwt_required()
def update_role():
    """更新角色"""
    data = request.json
    role_id = data.get('role_id')
    name = data.get('name')
    description = data.get('description')
    permissions = data.get('permissions')
    current_user_id = get_jwt_identity()
    current_user = User.get_user(current_user_id)
    
    try:
        result = role_services.update_role(current_user, role_id, name, description, permissions)
        return jsonify({"code": 200, "message": result}), 200
    except role_services.RoleServiceException as e:
        return jsonify({"code": e.code, "message": e.message}), e.code
    except permission_services.PermissionServiceException as e:
        return jsonify({"code": e.code, "message": e.message}), e.code
    except Exception as e:
        if DEBUG_MODE:
            return jsonify({"code": 500, "message": str(e)}), 500
        else:
            return jsonify({"code": 500, "message": "未知错误导致更新角色失败"}), 500


@role_blueprint.route('/delete', methods=['DELETE'])
@jwt_required()
def delete_role():
    """删除角色"""
    data = request.json
    role_id = data.get('role_id')
    current_user_id = get_jwt_identity()
    current_user = User.get_user(current_user_id)
    
    try:
        result = role_services.delete_role(current_user, role_id)
        return jsonify({"code": 200, "message": result}), 200
    except role_services.RoleServiceException as e:
        return jsonify({"code": e.code, "message": e.message}), e.code
    except permission_services.PermissionServiceException as e:
        return jsonify({"code": e.code, "message": e.message}), e.code
    except Exception as e:
        if DEBUG_MODE:
            return jsonify({"code": 500, "message": str(e)}), 500
        else:
            return jsonify({"code": 500, "message": "未知错误导致删除角色失败"}), 500


@role_blueprint.route('/get', methods=['GET'])
@jwt_required()
def get_role():
    """获取角色"""
    role_id = request.args.get('role_id', type=int)
    current_user_id = get_jwt_identity()
    current_user = User.get_user(current_user_id)
    
    try:
        result = role_services.get_role(current_user, role_id)
        return jsonify({"code": 200, "data": result.model_dump(), "message": "获取角色成功"}), 200
    except role_services.RoleServiceException as e:
        return jsonify({"code": e.code, "message": e.message}), e.code
    except permission_services.PermissionServiceException as e:
        return jsonify({"code": e.code, "message": e.message}), e.code
    except Exception as e:
        if DEBUG_MODE:
            return jsonify({"code": 500, "message": str(e)}), 500
        else:
            return jsonify({"code": 500, "message": "未知错误导致获取角色失败"}), 500


@role_blueprint.route('/list', methods=['GET'])
@jwt_required()
def get_roles_by_department():
    """获取部门角色列表"""
    department_id = request.args.get('department_id', type=int)
    current_user_id = get_jwt_identity()
    current_user = User.get_user(current_user_id)
    
    try:
        result = role_services.get_roles_by_department(current_user, department_id)
        # 将角色列表转换为字典列表
        roles_data = [role.model_dump() for role in result]
        return jsonify({"code": 200, "data": roles_data, "message": "获取角色列表成功"}), 200
    except role_services.RoleServiceException as e:
        return jsonify({"code": e.code, "message": e.message}), e.code
    except permission_services.PermissionServiceException as e:
        return jsonify({"code": e.code, "message": e.message}), e.code
    except Exception as e:
        if DEBUG_MODE:
            return jsonify({"code": 500, "message": str(e)}), 500
        else:
            return jsonify({"code": 500, "message": "未知错误导致获取角色列表失败"}), 500
@role_blueprint.route('/get_all_permissions', methods=['GET'])
@jwt_required()
def get_all_permissions():
    """获取所有权限"""
    current_user_id = get_jwt_identity()
    current_user = User.get_user(current_user_id)
    try:
        from models.core.permission import PermissionManager
        return jsonify({"code": 200, "data": PermissionManager.get_all_permissions(), "message": "获取所有角色成功"}), 200
    except Exception as e:
        if DEBUG_MODE:
            return jsonify({"code": 500, "message": str(e)}), 500
        else:
            return jsonify({"code": 500, "message": "未知错误导致获取所有权限失败"}), 500
