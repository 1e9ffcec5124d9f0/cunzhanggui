from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import Blueprint, request, jsonify
from typing import Optional
from core.configs import DEBUG_MODE
import services.core.internal_organization_services as internal_organization_services
import services.core.permission_services as permission_services
from models.core.user import User

internal_organization_blueprint = Blueprint('internal_organization', __name__, url_prefix='/api/internal_organization')


@internal_organization_blueprint.route('/create', methods=['POST'])
@jwt_required()
def create_internal_organization():
    """创建内部组织"""
    data = request.json
    name = data.get('name')
    department_id = data.get('department_id')
    
    current_user_id = get_jwt_identity()
    current_user = User.get_user(current_user_id)
    
    try:
        result = internal_organization_services.create_internal_organization(
            current_user=current_user,
            name=name,
            department_id=department_id
        )
        return jsonify({"code": 200, "message": result}), 200
    except internal_organization_services.InternalOrganizationServiceException as e:
        return jsonify({"code": e.code, "message": e.message}), e.code
    except permission_services.PermissionServiceException as e:
        return jsonify({"code": e.code, "message": e.message}), e.code
    except Exception as e:
        if DEBUG_MODE:
            return jsonify({"code": 500, "message": str(e)}), 500
        else:
            return jsonify({"code": 500, "message": "未知错误导致创建内部组织失败"}), 500


@internal_organization_blueprint.route('/update', methods=['PUT'])
@jwt_required()
def update_internal_organization():
    """更新内部组织"""
    data = request.json
    internal_organization_id = data.get('internal_organization_id')
    name = data.get('name')
    
    current_user_id = get_jwt_identity()
    current_user = User.get_user(current_user_id)
    
    try:
        result = internal_organization_services.update_internal_organization(
            current_user=current_user,
            internal_organization_id=internal_organization_id,
            name=name
        )
        return jsonify({"code": 200, "message": result}), 200
    except internal_organization_services.InternalOrganizationServiceException as e:
        return jsonify({"code": e.code, "message": e.message}), e.code
    except permission_services.PermissionServiceException as e:
        return jsonify({"code": e.code, "message": e.message}), e.code
    except Exception as e:
        if DEBUG_MODE:
            return jsonify({"code": 500, "message": str(e)}), 500
        else:
            return jsonify({"code": 500, "message": "未知错误导致更新内部组织失败"}), 500


@internal_organization_blueprint.route('/delete', methods=['DELETE'])
@jwt_required()
def delete_internal_organization():
    """删除内部组织"""
    data = request.json
    internal_organization_id = data.get('internal_organization_id')
    
    current_user_id = get_jwt_identity()
    current_user = User.get_user(current_user_id)
    
    try:
        result = internal_organization_services.delete_internal_organization(
            current_user=current_user,
            internal_organization_id=internal_organization_id
        )
        return jsonify({"code": 200, "message": result}), 200
    except internal_organization_services.InternalOrganizationServiceException as e:
        return jsonify({"code": e.code, "message": e.message}), e.code
    except permission_services.PermissionServiceException as e:
        return jsonify({"code": e.code, "message": e.message}), e.code
    except Exception as e:
        if DEBUG_MODE:
            return jsonify({"code": 500, "message": str(e)}), 500
        else:
            return jsonify({"code": 500, "message": "未知错误导致删除内部组织失败"}), 500


@internal_organization_blueprint.route('/get', methods=['GET'])
@jwt_required()
def get_internal_organization():
    """获取内部组织"""
    internal_organization_id = request.args.get('internal_organization_id', type=int)
    
    current_user_id = get_jwt_identity()
    current_user = User.get_user(current_user_id)
    
    try:
        result = internal_organization_services.get_internal_organization(
            current_user=current_user,
            internal_organization_id=internal_organization_id
        )
        return jsonify({"code": 200, "data": result.model_dump(), "message": "获取内部组织成功"}), 200
    except internal_organization_services.InternalOrganizationServiceException as e:
        return jsonify({"code": e.code, "message": e.message}), e.code
    except permission_services.PermissionServiceException as e:
        return jsonify({"code": e.code, "message": e.message}), e.code
    except Exception as e:
        if DEBUG_MODE:
            return jsonify({"code": 500, "message": str(e)}), 500
        else:
            return jsonify({"code": 500, "message": "未知错误导致获取内部组织失败"}), 500


@internal_organization_blueprint.route('/list', methods=['GET'])
@jwt_required()
def get_internal_organizations_by_department():
    """获取部门内部组织列表"""
    department_id = request.args.get('department_id', type=int)
    
    current_user_id = get_jwt_identity()
    current_user = User.get_user(current_user_id)
    
    try:
        result = internal_organization_services.get_internal_organizations_by_department(
            current_user=current_user,
            department_id=department_id
        )
        # 将内部组织列表转换为字典列表
        internal_organizations_data = [internal_organization.model_dump() for internal_organization in result]
        return jsonify({"code": 200, "data": internal_organizations_data, "message": "获取内部组织列表成功"}), 200
    except internal_organization_services.InternalOrganizationServiceException as e:
        return jsonify({"code": e.code, "message": e.message}), e.code
    except permission_services.PermissionServiceException as e:
        return jsonify({"code": e.code, "message": e.message}), e.code
    except Exception as e:
        if DEBUG_MODE:
            return jsonify({"code": 500, "message": str(e)}), 500
        else:
            return jsonify({"code": 500, "message": "未知错误导致获取内部组织列表失败"}), 500 