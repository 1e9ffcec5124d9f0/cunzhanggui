from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import Blueprint, request, jsonify
from typing import Optional
from core.configs import DEBUG_MODE
import services.core.internal_organization_to_user_services as internal_organization_to_user_services
import services.core.permission_services as permission_services
from models.core.user import User

internal_organization_to_user_blueprint = Blueprint('internal_organization_to_user', __name__, url_prefix='/api/internal_organization_to_user')


@internal_organization_to_user_blueprint.route('/add_user', methods=['POST'])
@jwt_required()
def add_user_to_internal_organization():
    """添加用户到内部组织"""
    data = request.json
    internal_organization_id = data.get('internal_organization_id')
    user_id = data.get('user_id')
    
    current_user_id = get_jwt_identity()
    current_user = User.get_user(current_user_id)
    
    try:
        result = internal_organization_to_user_services.add_user_to_internal_organization(
            current_user=current_user,
            internal_organization_id=internal_organization_id,
            user_id=user_id
        )
        return jsonify({"code": 200, "message": result}), 200
    except internal_organization_to_user_services.InternalOrganizationToUserServiceException as e:
        return jsonify({"code": e.code, "message": e.message}), e.code
    except permission_services.PermissionServiceException as e:
        return jsonify({"code": e.code, "message": e.message}), e.code
    except Exception as e:
        if DEBUG_MODE:
            return jsonify({"code": 500, "message": str(e)}), 500
        else:
            return jsonify({"code": 500, "message": "未知错误导致添加用户到内部组织失败"}), 500


@internal_organization_to_user_blueprint.route('/remove_user', methods=['DELETE'])
@jwt_required()
def remove_user_from_internal_organization():
    """从内部组织移除用户"""
    data = request.json
    internal_organization_id = data.get('internal_organization_id')
    user_id = data.get('user_id')
    
    current_user_id = get_jwt_identity()
    current_user = User.get_user(current_user_id)
    
    try:
        result = internal_organization_to_user_services.remove_user_from_internal_organization(
            current_user=current_user,
            internal_organization_id=internal_organization_id,
            user_id=user_id
        )
        return jsonify({"code": 200, "message": result}), 200
    except internal_organization_to_user_services.InternalOrganizationToUserServiceException as e:
        return jsonify({"code": e.code, "message": e.message}), e.code
    except permission_services.PermissionServiceException as e:
        return jsonify({"code": e.code, "message": e.message}), e.code
    except Exception as e:
        if DEBUG_MODE:
            return jsonify({"code": 500, "message": str(e)}), 500
        else:
            return jsonify({"code": 500, "message": "未知错误导致从内部组织移除用户失败"}), 500


@internal_organization_to_user_blueprint.route('/get_users_by_organization', methods=['GET'])
@jwt_required()
def get_users_by_internal_organization():
    """获取内部组织中的用户关系列表"""
    internal_organization_id = request.args.get('internal_organization_id', type=int)
    
    current_user_id = get_jwt_identity()
    current_user = User.get_user(current_user_id)
    
    try:
        result = internal_organization_to_user_services.get_users_by_internal_organization(
            current_user=current_user,
            internal_organization_id=internal_organization_id
        )
        # 将内部组织与用户关系列表转换为字典列表
        relationships_data = [relationship.model_dump() for relationship in result]
        return jsonify({"code": 200, "data": relationships_data, "message": "获取内部组织用户关系列表成功"}), 200
    except internal_organization_to_user_services.InternalOrganizationToUserServiceException as e:
        return jsonify({"code": e.code, "message": e.message}), e.code
    except permission_services.PermissionServiceException as e:
        return jsonify({"code": e.code, "message": e.message}), e.code
    except Exception as e:
        if DEBUG_MODE:
            return jsonify({"code": 500, "message": str(e)}), 500
        else:
            return jsonify({"code": 500, "message": "未知错误导致获取内部组织用户关系列表失败"}), 500


@internal_organization_to_user_blueprint.route('/get_organizations_by_user', methods=['GET'])
@jwt_required()
def get_internal_organizations_by_user():
    """获取用户所属内部组织关系列表"""
    user_id = request.args.get('user_id', type=int)
    
    current_user_id = get_jwt_identity()
    current_user = User.get_user(current_user_id)
    
    try:
        result = internal_organization_to_user_services.get_internal_organizations_by_user(
            current_user=current_user,
            user_id=user_id
        )
        # 将内部组织与用户关系列表转换为字典列表
        relationships_data = [relationship.model_dump() for relationship in result]
        return jsonify({"code": 200, "data": relationships_data, "message": "获取用户内部组织关系列表成功"}), 200
    except internal_organization_to_user_services.InternalOrganizationToUserServiceException as e:
        return jsonify({"code": e.code, "message": e.message}), e.code
    except permission_services.PermissionServiceException as e:
        return jsonify({"code": e.code, "message": e.message}), e.code
    except Exception as e:
        if DEBUG_MODE:
            return jsonify({"code": 500, "message": str(e)}), 500
        else:
            return jsonify({"code": 500, "message": "未知错误导致获取用户内部组织关系列表失败"}), 500 