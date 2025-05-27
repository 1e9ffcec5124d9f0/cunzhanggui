from flask_jwt_extended import jwt_required,get_jwt_identity
from flask import Blueprint, request,jsonify
from core.configs import DEBUG_MODE
import services.core.department_services as department_services
import services.core.permission_services as permission_services
from models.core.user import User
department_blueprint=Blueprint('department',__name__,url_prefix='/api/department')

@department_blueprint.route('/create',methods=['POST'])
@jwt_required()
def create_department():
    """创建部门"""
    data=request.json
    name=data.get('name')
    description=data.get('description')
    manager_name=data.get('manager_name')
    manager_phone=data.get('manager_phone')
    current_user_id=get_jwt_identity()
    current_user=User.get_user(current_user_id)
    try:
        result=department_services.create_department(current_user,name,description,manager_name,manager_phone)
        return jsonify({"code":200,"message":result}),200
    except department_services.DepartmentServiceException as e:
        return jsonify({"code":e.code,"message":e.message}),e.code
    except permission_services.PermissionServiceException as e:
        return jsonify({"code":e.code,"message":e.message}),e.code
    except Exception as e:
        if DEBUG_MODE:
            return jsonify({"code":500,"message":str(e)}),500
        else:
            return jsonify({"code":500,"message":"未知错误导致创建部门失败"}),500


@department_blueprint.route('/update',methods=['PUT'])
@jwt_required()
def update_department():
    """更新部门"""
    data=request.json
    department_id=data.get('department_id')
    name=data.get('name')
    description=data.get('description')
    manager_name=data.get('manager_name')
    manager_phone=data.get('manager_phone')
    current_user_id=get_jwt_identity()
    current_user=User.get_user(current_user_id)
    try:
        result=department_services.update_department(current_user,department_id,name,description,manager_name,manager_phone)
        return jsonify({"code":200,"message":result}),200
    except department_services.DepartmentServiceException as e:
        return jsonify({"code":e.code,"message":e.message}),e.code
    except permission_services.PermissionServiceException as e:
        return jsonify({"code":e.code,"message":e.message}),e.code
    except Exception as e:
        if DEBUG_MODE:
            return jsonify({"code":500,"message":str(e)}),500
        else:
            return jsonify({"code":500,"message":"未知错误导致更新部门失败"}),500


@department_blueprint.route('/delete',methods=['DELETE'])
@jwt_required()
def delete_department():
    """删除部门"""
    data=request.json
    department_id=data.get('department_id')
    current_user_id=get_jwt_identity()
    current_user=User.get_user(current_user_id)
    try:
        result=department_services.delete_department(current_user,department_id)
        return jsonify({"code":200,"message":result}),200
    except department_services.DepartmentServiceException as e:
        return jsonify({"code":e.code,"message":e.message}),e.code
    except permission_services.PermissionServiceException as e:
        return jsonify({"code":e.code,"message":e.message}),e.code
    except Exception as e:
        if DEBUG_MODE:
            return jsonify({"code":500,"message":str(e)}),500
        else:
            return jsonify({"code":500,"message":"未知错误导致删除部门失败"}),500


@department_blueprint.route('/get', methods=['GET'])
@jwt_required()
def get_department():
    """获取部门"""
    department_id = request.args.get('department_id', type=int)
    current_user_id = get_jwt_identity()
    current_user = User.get_user(current_user_id)
    try:
        result = department_services.get_department(current_user, department_id)
        return jsonify({"code": 200, "data": result.model_dump(), "message": "获取部门成功"}), 200
    except department_services.DepartmentServiceException as e:
        return jsonify({"code": e.code, "message": e.message}), e.code
    except permission_services.PermissionServiceException as e:
        return jsonify({"code": e.code, "message": e.message}), e.code
    except Exception as e:
        if DEBUG_MODE:
            return jsonify({"code": 500, "message": str(e)}), 500
        else:
            return jsonify({"code": 500, "message": "未知错误导致获取部门失败"}), 500

@department_blueprint.route('/get_my_department', methods=['GET'])
@jwt_required()
def get_my_department():
    """获取当前用户部门"""
    current_user_id = get_jwt_identity()
    current_user = User.get_user(current_user_id)
    try:
        result = department_services.get_department(current_user,current_user.department_id)
        return jsonify({"code": 200, "data": result.model_dump(), "message": "获取部门成功"}), 200
    except department_services.DepartmentServiceException as e:
        return jsonify({"code":e.code,"message":e.message}),e.code
    except permission_services.PermissionServiceException as e:
        return jsonify({"code":e.code,"message":e.message}),e.code
    except Exception as e:
        if DEBUG_MODE:
            return jsonify({"code":500,"message":str(e)}),500
        else:
            return jsonify({"code":500,"message":"未知错误导致获取当前用户部门失败"}),500

@department_blueprint.route('/tree', methods=['GET'])
@jwt_required()
def get_department_tree():
    """获取部门树"""
    current_user_id = get_jwt_identity()
    current_user = User.get_user(current_user_id)
    try:
        result = department_services.get_department_tree(current_user)
        return jsonify({"code": 200, "data": result, "message": "获取部门树成功"}), 200
    except department_services.DepartmentServiceException as e:
        return jsonify({"code": e.code, "message": e.message}), e.code
    except permission_services.PermissionServiceException as e:
        return jsonify({"code": e.code, "message": e.message}), e.code
    except Exception as e:
        if DEBUG_MODE:
            return jsonify({"code": 500, "message": str(e)}), 500
        else:
            return jsonify({"code": 500, "message": "未知错误导致获取部门树失败"}), 500




