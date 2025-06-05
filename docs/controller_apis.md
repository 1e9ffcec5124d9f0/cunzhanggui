# 控制器接口文档

本文档详细描述了项目中所有控制器的接口，包括请求参数、返回数据结构和错误处理。

## 1. 密码学控制器 (crypto_controllers.py)

### 1.1 获取公钥
- **接口路径**: `GET /api/crypto/get_public_key`
- **描述**: 获取SM2加密算法的公钥
- **权限要求**: 无需认证
- **请求参数**: 无

**返回数据结构**:
```json
{
    "code": 200,
    "message": "获取公钥成功",
    "data": {
        "public_key": "04abc123...def789"  // 十六进制格式的SM2公钥
    }
}
```

## 2. 部门控制器 (department_controllers.py)

### 2.1 创建部门
- **接口路径**: `POST /api/department/create`
- **描述**: 创建新的部门
- **权限要求**: 需要JWT认证，需要创建部门权限

**请求参数**:
```json
{
    "name": "部门名称",
    "description": "部门描述",
    "manager_name": "负责人姓名",
    "manager_phone": "负责人电话"
}
```

**返回数据结构**:
- 成功时:
```json
{
    "code": 200,
    "message": "用户创建成功"
}
```
- 失败时:
```json
{
    "code": 错误代码,
    "message": "错误信息"
}
```

### 2.2 更新部门
- **接口路径**: `PUT /api/department/update`
- **描述**: 更新部门信息
- **权限要求**: 需要JWT认证，需要修改部门权限

**请求参数**:
```json
{
    "department_id": 1,
    "name": "新部门名称",
    "description": "新部门描述",
    "manager_name": "新负责人姓名",
    "manager_phone": "新负责人电话"
}
```

**返回数据结构**:
- 成功时:
```json
{
    "code": 200,
    "message": "部门更新成功"
}
```

### 2.3 删除部门
- **接口路径**: `DELETE /api/department/delete`
- **描述**: 删除指定部门
- **权限要求**: 需要JWT认证，需要删除部门权限

**请求参数**:
```json
{
    "department_id": 1
}
```

**返回数据结构**:
- 成功时:
```json
{
    "code": 200,
    "message": "部门删除成功"
}
```

### 2.4 获取部门
- **接口路径**: `GET /api/department/get`
- **描述**: 获取指定部门的详细信息
- **权限要求**: 需要JWT认证，需要查看部门权限

**请求参数**:
- `department_id` (query参数): 部门ID

**返回数据结构**:
- 成功时:
```json
{
    "code": 200,
    "message": "获取部门成功",
    "data": {
        "id": 1,
        "name": "部门名称",
        "level": 1,
        "parent_id": 0,
        "description": "部门描述",
        "manager_name": "负责人姓名",
        "manager_phone": "负责人电话",
        "created_at": "2024-01-01T00:00:00.000Z",
        "updated_at": "2024-01-01T00:00:00.000Z"
    }
}
```

### 2.5 获取当前用户部门
- **接口路径**: `GET /api/department/get_my_department`
- **描述**: 获取当前登录用户所属部门的信息
- **权限要求**: 需要JWT认证

**请求参数**: 无

**返回数据结构**:
- 成功时:
```json
{
    "code": 200,
    "message": "获取部门成功",
    "data": {
        "id": 1,
        "name": "部门名称",
        "level": 1,
        "parent_id": 0,
        "description": "部门描述",
        "manager_name": "负责人姓名",
        "manager_phone": "负责人电话",
        "created_at": "2024-01-01T00:00:00.000Z",
        "updated_at": "2024-01-01T00:00:00.000Z"
    }
}
```

### 2.6 获取部门树
- **接口路径**: `GET /api/department/tree`
- **描述**: 获取部门的树形结构
- **权限要求**: 需要JWT认证，需要查看部门权限

**请求参数**: 无

**返回数据结构**:
- 成功时:
```json
{
    "code": 200,
    "message": "获取部门树成功",
    "data": [
        {
            "id": 1,
            "name": "根部门",
            "level": 0,
            "parent_id": null,
            "description": "根部门描述",
            "manager_name": "根部门负责人",
            "manager_phone": "联系电话",
            "created_at": "2024-01-01T00:00:00.000Z",
            "updated_at": "2024-01-01T00:00:00.000Z",
            "children": [
                {
                    "id": 2,
                    "name": "子部门1",
                    "level": 1,
                    "parent_id": 1,
                    "description": "子部门描述",
                    "manager_name": "子部门负责人",
                    "manager_phone": "联系电话",
                    "created_at": "2024-01-01T00:00:00.000Z",
                    "updated_at": "2024-01-01T00:00:00.000Z",
                    "children": []
                }
            ]
        }
    ]
}
```

## 3. 内部组织控制器 (internal_organization_controllers.py)

### 3.1 创建内部组织
- **接口路径**: `POST /api/internal_organization/create`
- **描述**: 在指定部门下创建内部组织
- **权限要求**: 需要JWT认证，需要创建内部组织权限

**请求参数**:
```json
{
    "name": "内部组织名称",
    "department_id": 1
}
```

**返回数据结构**:
- 成功时:
```json
{
    "code": 200,
    "message": "内部组织创建成功"
}
```

### 3.2 更新内部组织
- **接口路径**: `PUT /api/internal_organization/update`
- **描述**: 更新内部组织信息
- **权限要求**: 需要JWT认证，需要修改内部组织权限

**请求参数**:
```json
{
    "internal_organization_id": 1,
    "name": "新的内部组织名称"
}
```

**返回数据结构**:
- 成功时:
```json
{
    "code": 200,
    "message": "内部组织更新成功"
}
```

### 3.3 删除内部组织
- **接口路径**: `DELETE /api/internal_organization/delete`
- **描述**: 删除指定的内部组织
- **权限要求**: 需要JWT认证，需要删除内部组织权限

**请求参数**:
```json
{
    "internal_organization_id": 1
}
```

**返回数据结构**:
- 成功时:
```json
{
    "code": 200,
    "message": "内部组织删除成功"
}
```

### 3.4 获取内部组织
- **接口路径**: `GET /api/internal_organization/get`
- **描述**: 获取指定内部组织的详细信息
- **权限要求**: 需要JWT认证，需要查看内部组织权限

**请求参数**:
- `internal_organization_id` (query参数): 内部组织ID

**返回数据结构**:
- 成功时:
```json
{
    "code": 200,
    "message": "获取内部组织成功",
    "data": {
        "id": 1,
        "name": "内部组织名称",
        "department_id": 1,
        "created_at": "2024-01-01T00:00:00.000Z",
        "updated_at": "2024-01-01T00:00:00.000Z"
    }
}
```

### 3.5 获取部门内部组织列表
- **接口路径**: `GET /api/internal_organization/list`
- **描述**: 获取指定部门下的所有内部组织
- **权限要求**: 需要JWT认证，需要查看内部组织权限

**请求参数**:
- `department_id` (query参数): 部门ID

**返回数据结构**:
- 成功时:
```json
{
    "code": 200,
    "message": "获取内部组织列表成功",
    "data": [
        {
            "id": 1,
            "name": "内部组织1",
            "department_id": 1,
            "created_at": "2024-01-01T00:00:00.000Z",
            "updated_at": "2024-01-01T00:00:00.000Z"
        },
        {
            "id": 2,
            "name": "内部组织2",
            "department_id": 1,
            "created_at": "2024-01-01T00:00:00.000Z",
            "updated_at": "2024-01-01T00:00:00.000Z"
        }
    ]
}
```

## 4. 内部组织用户关系控制器 (internal_organization_to_user_controllers.py)

### 4.1 添加用户到内部组织
- **接口路径**: `POST /api/internal_organization_to_user/add_user`
- **描述**: 将用户添加到指定的内部组织
- **权限要求**: 需要JWT认证，需要管理内部组织权限

**请求参数**:
```json
{
    "internal_organization_id": 1,
    "user_id": 1
}
```

**返回数据结构**:
- 成功时:
```json
{
    "code": 200,
    "message": "用户添加到内部组织成功"
}
```

### 4.2 从内部组织移除用户
- **接口路径**: `DELETE /api/internal_organization_to_user/remove_user`
- **描述**: 从内部组织中移除指定用户
- **权限要求**: 需要JWT认证，需要管理内部组织权限

**请求参数**:
```json
{
    "internal_organization_id": 1,
    "user_id": 1
}
```

**返回数据结构**:
- 成功时:
```json
{
    "code": 200,
    "message": "用户从内部组织移除成功"
}
```

### 4.3 获取内部组织中的用户关系列表
- **接口路径**: `GET /api/internal_organization_to_user/get_users_by_organization`
- **描述**: 获取指定内部组织中的所有用户关系
- **权限要求**: 需要JWT认证，需要查看内部组织权限

**请求参数**:
- `internal_organization_id` (query参数): 内部组织ID

**返回数据结构**:
- 成功时:
```json
{
    "code": 200,
    "message": "获取内部组织用户关系列表成功",
    "data": [
        {
            "id": 1,
            "internal_organization_id": 1,
            "user_id": 1
        },
        {
            "id": 2,
            "internal_organization_id": 1,
            "user_id": 2
        }
    ]
}
```

### 4.4 获取用户所属内部组织关系列表
- **接口路径**: `GET /api/internal_organization_to_user/get_organizations_by_user`
- **描述**: 获取指定用户所属的所有内部组织关系
- **权限要求**: 需要JWT认证，需要查看内部组织权限

**请求参数**:
- `user_id` (query参数): 用户ID

**返回数据结构**:
- 成功时:
```json
{
    "code": 200,
    "message": "获取用户内部组织关系列表成功",
    "data": [
        {
            "id": 1,
            "internal_organization_id": 1,
            "user_id": 1
        },
        {
            "id": 2,
            "internal_organization_id": 2,
            "user_id": 1
        }
    ]
}
```

## 5. 角色控制器 (role_controllers.py)

### 5.1 创建角色
- **接口路径**: `POST /api/role/create`
- **描述**: 创建新角色
- **权限要求**: 需要JWT认证，需要创建角色权限

**请求参数**:
```json
{
    "name": "角色名称",
    "description": "角色描述",
    "permissions": ["permission1", "permission2"],
    "department_id": 1
}
```

**返回数据结构**:
- 成功时:
```json
{
    "code": 200,
    "message": "角色创建成功"
}
```

### 5.2 更新角色
- **接口路径**: `PUT /api/role/update`
- **描述**: 更新角色信息
- **权限要求**: 需要JWT认证，需要修改角色权限

**请求参数**:
```json
{
    "role_id": 1,
    "name": "新角色名称",
    "description": "新角色描述",
    "permissions": ["permission1", "permission3"]
}
```

**返回数据结构**:
- 成功时:
```json
{
    "code": 200,
    "message": "角色更新成功"
}
```

### 5.3 删除角色
- **接口路径**: `DELETE /api/role/delete`
- **描述**: 删除指定角色
- **权限要求**: 需要JWT认证，需要删除角色权限

**请求参数**:
```json
{
    "role_id": 1
}
```

**返回数据结构**:
- 成功时:
```json
{
    "code": 200,
    "message": "角色删除成功"
}
```

### 5.4 获取角色
- **接口路径**: `GET /api/role/get`
- **描述**: 获取指定角色的详细信息
- **权限要求**: 需要JWT认证，需要查看角色权限

**请求参数**:
- `role_id` (query参数): 角色ID

**返回数据结构**:
- 成功时:
```json
{
    "code": 200,
    "message": "获取角色成功",
    "data": {
        "id": 1,
        "name": "角色名称",
        "description": "角色描述",
        "permissions": ["permission1", "permission2"],
        "department_id": 1,
        "created_at": "2024-01-01T00:00:00.000Z",
        "updated_at": "2024-01-01T00:00:00.000Z"
    }
}
```

### 5.5 获取部门角色列表
- **接口路径**: `GET /api/role/list`
- **描述**: 获取指定部门的所有角色
- **权限要求**: 需要JWT认证，需要查看角色权限

**请求参数**:
- `department_id` (query参数): 部门ID

**返回数据结构**:
- 成功时:
```json
{
    "code": 200,
    "message": "获取角色列表成功",
    "data": [
        {
            "id": 1,
            "name": "角色1",
            "description": "角色1描述",
            "permissions": ["permission1", "permission2"],
            "department_id": 1,
            "created_at": "2024-01-01T00:00:00.000Z",
            "updated_at": "2024-01-01T00:00:00.000Z"
        },
        {
            "id": 2,
            "name": "角色2",
            "description": "角色2描述",
            "permissions": ["permission3", "permission4"],
            "department_id": 1,
            "created_at": "2024-01-01T00:00:00.000Z",
            "updated_at": "2024-01-01T00:00:00.000Z"
        }
    ]
}
```

### 5.6 获取所有权限
- **接口路径**: `GET /api/role/get_all_permissions`
- **描述**: 获取系统中所有可用的权限列表
- **权限要求**: 需要JWT认证

**请求参数**: 无

**返回数据结构**:
- 成功时:
```json
{
    "code": 200,
    "message": "获取所有角色成功",
    "data": ["permission1", "permission2", "permission3", "permission4"]
}
```

## 6. 用户控制器 (user_controllers.py)

### 6.1 创建用户
- **接口路径**: `POST /api/user/create`
- **描述**: 创建新用户
- **权限要求**: 需要JWT认证，需要创建用户权限

**请求参数**:
```json
{
    "username": "用户名",
    "password": "密码",
    "id_card_number": "身份证号码",
    "phone_number": "手机号码",
    "real_name": "真实姓名",
    "department_id": 1
}
```

**返回数据结构**:
- 成功时:
```json
{
    "code": 200,
    "message": "用户创建成功"
}
```

### 6.2 更新用户
- **接口路径**: `PUT /api/user/update`
- **描述**: 更新用户信息
- **权限要求**: 需要JWT认证，需要修改用户权限

**请求参数**:
```json
{
    "user_id": 1,
    "username": "新用户名",
    "id_card_number": "新身份证号码",
    "phone_number": "新手机号码",
    "real_name": "新真实姓名",
    "department_id": 2,
    "role_ids": [1, 2]
}
```

**返回数据结构**:
- 成功时:
```json
{
    "code": 200,
    "message": "用户更新成功"
}
```

### 6.3 删除用户
- **接口路径**: `DELETE /api/user/delete`
- **描述**: 删除指定用户
- **权限要求**: 需要JWT认证，需要删除用户权限

**请求参数**:
```json
{
    "user_id": 1
}
```

**返回数据结构**:
- 成功时:
```json
{
    "code": 200,
    "message": "用户删除成功"
}
```

### 6.4 获取用户
- **接口路径**: `GET /api/user/get`
- **描述**: 获取指定用户的详细信息
- **权限要求**: 需要JWT认证，需要查看用户权限

**请求参数**:
- `user_id` (query参数, 可选): 用户ID
- `username` (query参数, 可选): 用户名

**返回数据结构**:
- 成功时:
```json
{
    "code": 200,
    "message": "获取用户成功",
    "data": {
        "id": 1,
        "username": "用户名",
        "password_hash": "加密后的密码哈希",
        "id_card_number": "身份证号码",
        "phone_number": "手机号码",
        "real_name": "真实姓名",
        "department_id": 1,
        "login_attempts": 0,
        "role_ids": [1, 2],
        "created_at": "2024-01-01T00:00:00.000Z",
        "updated_at": "2024-01-01T00:00:00.000Z"
    }
}
```

### 6.5 获取当前用户信息
- **接口路径**: `GET /api/user/get_current`
- **描述**: 获取当前登录用户的信息
- **权限要求**: 需要JWT认证

**请求参数**: 无

**返回数据结构**:
- 成功时:
```json
{
    "code": 200,
    "message": "获取当前用户信息成功",
    "data": {
        "id": 1,
        "username": "用户名",
        "id_card_number": "身份证号码",
        "phone_number": "手机号码",
        "real_name": "真实姓名",
        "department_id": 1,
        "login_attempts": 0,
        "role_ids": [1, 2],
        "created_at": "2024-01-01T00:00:00.000Z",
        "updated_at": "2024-01-01T00:00:00.000Z"
    }
}
```
**注意**: 返回的用户信息中不包含 `password_hash` 字段，以保护用户隐私。

### 6.6 根据部门获取用户列表
- **接口路径**: `GET /api/user/list`
- **描述**: 获取指定部门的所有用户
- **权限要求**: 需要JWT认证，需要查看用户权限

**请求参数**:
- `department_id` (query参数): 部门ID

**返回数据结构**:
- 成功时:
```json
{
    "code": 200,
    "message": "获取用户列表成功",
    "data": [
        {
            "id": 1,
            "username": "用户1",
            "password_hash": "加密后的密码哈希",
            "id_card_number": "身份证号码1",
            "phone_number": "手机号码1",
            "real_name": "真实姓名1",
            "department_id": 1,
            "login_attempts": 0,
            "role_ids": [1],
            "created_at": "2024-01-01T00:00:00.000Z",
            "updated_at": "2024-01-01T00:00:00.000Z"
        },
        {
            "id": 2,
            "username": "用户2",
            "password_hash": "加密后的密码哈希",
            "id_card_number": "身份证号码2",
            "phone_number": "手机号码2",
            "real_name": "真实姓名2",
            "department_id": 1,
            "login_attempts": 0,
            "role_ids": [2],
            "created_at": "2024-01-01T00:00:00.000Z",
            "updated_at": "2024-01-01T00:00:00.000Z"
        }
    ]
}
```

### 6.7 修改用户密码
- **接口路径**: `PUT /api/user/change_password`
- **描述**: 修改指定用户的密码
- **权限要求**: 需要JWT认证，需要修改用户密码权限

**请求参数**:
```json
{
    "user_id": 1,
    "new_password": "新密码"
}
```

**返回数据结构**:
- 成功时:
```json
{
    "code": 200,
    "message": "密码修改成功"
}
```

### 6.8 用户登录
- **接口路径**: `POST /api/user/login`
- **描述**: 用户登录验证
- **权限要求**: 无需认证

**请求参数**:
```json
{
    "username": "用户名",
    "password": "密码"
}
```

**返回数据结构**:
- 成功时:
```json
{
    "code": 200,
    "message": "登录成功",
    "data": {
        "access_token": "JWT令牌字符串"
    }
}
```

## 错误码说明

所有接口都遵循统一的错误响应格式：

```json
{
    "code": 错误代码,
    "message": "错误描述信息"
}
```

常见错误码：
- `200`: 操作成功
- `400`: 请求参数错误
- `401`: 未授权，需要登录
- `403`: 权限不足
- `404`: 资源不存在
- `500`: 服务器内部错误

## 权限系统说明

本系统使用基于角色的权限控制(RBAC)：
1. 用户通过JWT令牌进行身份认证
2. 用户可以拥有多个角色 (`role_ids` 字段)
3. 角色包含权限列表 (`permissions` 字段)
4. 接口调用时会检查用户是否具有相应权限

## 数据类型说明

- **datetime**: 时间戳格式为ISO 8601标准，如 `"2024-01-01T00:00:00.000Z"`
- **JSON数组**: 如 `role_ids` 和 `permissions` 字段存储为JSON数组格式
- **外键关系**: 
  - `department_id` 关联到部门表
  - `user_id` 关联到用户表
  - `internal_organization_id` 关联到内部组织表
  - `role_id` 关联到角色表