# Role 角色模型文档

## 概述

`Role` 模型是基于 SQLModel 构建的角色管理系统核心模型，用于管理系统中的角色信息和权限分配。该模型与部门模型关联，支持基于部门的角色管理，是系统权限控制的重要组成部分。

## 模型结构

### 数据表信息
- **表名**: `roles`
- **主键**: `id`
- **外键**: `department_id` (关联到 `departments.id`)

### 字段说明

| 字段名 | 类型 | 约束 | 描述 |
|--------|------|------|------|
| `id` | `Optional[int]` | 主键，自增 | 角色唯一标识符 |
| `name` | `str` | 必填，索引 | 角色名称 |
| `description` | `Optional[str]` | 可选，默认空字符串 | 角色描述信息 |
| `permissions` | `List[str]` | JSON类型，默认空列表 | 角色拥有的权限列表 |
| `department_id` | `int` | 外键，必填 | 所属部门ID，关联到departments表 |
| `created_at` | `datetime` | 自动生成 | 创建时间（UTC时区） |
| `updated_at` | `datetime` | 自动生成 | 更新时间（UTC时区） |

## 异常处理

### RoleModelException

自定义异常类，用于处理角色模型相关的异常情况。

**属性**:
- `code`: 错误代码
- `message`: 错误信息

**构造函数**:
```python
def __init__(self, code: int, message: str)
```

## 类方法详解

### 1. create() - 创建角色

```python
@classmethod
def create(cls, name: str, department_id: int, 
          description: Optional[str] = None, 
          permissions: List[str] = []) -> Dict[str, str]
```

**功能**: 创建新的角色记录

**参数**:
- `name` (str): 角色名称，必填
- `department_id` (int): 所属部门ID，必填
- `description` (Optional[str]): 角色描述，可选
- `permissions` (List[str]): 角色权限列表，默认为空列表

**返回值**: 
- 成功: `{'success': "角色创建成功"}`

**异常**:
- `RoleModelException`: 
  - 404: 指定的部门不存在
  - 500: 角色创建失败

**业务逻辑**:
1. 验证指定的部门是否存在
2. 创建角色记录
3. 提交事务

**使用示例**:
```python
try:
    result = Role.create(
        name="系统管理员",
        department_id=1,
        description="拥有系统全部管理权限",
        permissions=["user.create", "user.read", "user.update", "user.delete"]
    )
    print(result)  # {'success': '角色创建成功'}
except RoleModelException as e:
    print(f"创建失败: {e.message}")
```

### 2. update() - 更新角色

```python
@classmethod
def update(cls, role_id: int, name: Optional[str] = None,
          description: Optional[str] = None, 
          permissions: Optional[List[str]] = None) -> Dict[str, str]
```

**功能**: 更新指定角色的信息

**参数**:
- `role_id` (int): 要更新的角色ID，必填
- `name` (Optional[str]): 角色名称，可选
- `description` (Optional[str]): 角色描述，可选
- `permissions` (Optional[List[str]]): 权限列表，可选

**返回值**: 
- 成功: `{'success': "角色更新成功"}`

**异常**:
- `RoleModelException`: 
  - 404: 指定的角色不存在
  - 500: 角色更新失败

**注意事项**:
- 只更新传入的非空参数
- 自动更新 `updated_at` 时间戳

**使用示例**:
```python
try:
    result = Role.update(
        role_id=1,
        name="高级管理员",
        permissions=["user.create", "user.read", "department.create"]
    )
    print(result)  # {'success': '角色更新成功'}
except RoleModelException as e:
    print(f"更新失败: {e.message}")
```

### 3. delete() - 删除角色

```python
@classmethod
def delete(cls, role_id: int) -> Dict[str, str]
```

**功能**: 删除指定的角色记录

**参数**:
- `role_id` (int): 要删除的角色ID

**返回值**: 
- 成功: `{'success': "角色删除成功"}`

**异常**:
- `RoleModelException`: 
  - 404: 指定的角色不存在
  - 500: 角色删除失败

**注意事项**: 
- 删除角色前应确保没有用户关联该角色
- 删除操作不可逆，请谨慎使用

**使用示例**:
```python
try:
    result = Role.delete(role_id=1)
    print(result)  # {'success': '角色删除成功'}
except RoleModelException as e:
    print(f"删除失败: {e.message}")
```

### 4. get_role() - 获取单个角色

```python
@classmethod
def get_role(cls, role_id: int) -> Dict[str, str]
```

**功能**: 根据角色ID获取角色详细信息

**参数**:
- `role_id` (int): 角色ID

**返回值**: 包含角色完整信息的字典
```python
{
    "id": int,
    "name": str,
    "description": str,
    "permissions": List[str],
    "department_id": int,
    "created_at": datetime,
    "updated_at": datetime
}
```

**异常**:
- `RoleModelException`: 
  - 404: 指定的角色不存在
  - 500: 获取角色失败

**使用示例**:
```python
try:
    role = Role.get_role(role_id=1)
    print(f"角色名称: {role['name']}")
    print(f"角色权限: {role['permissions']}")
    print(f"所属部门: {role['department_id']}")
except RoleModelException as e:
    print(f"获取失败: {e.message}")
```

### 5. get_role_by_department_id() - 根据部门获取角色列表

```python
@classmethod
def get_role_by_department_id(cls, department_id: int) -> List[Dict[str, str]]
```

**功能**: 根据部门ID获取该部门下的所有角色列表

**参数**:
- `department_id` (int): 部门ID

**返回值**: 角色信息列表，每个元素包含完整的角色信息字典

**异常**:
- `RoleModelException`: 获取失败时抛出

**使用示例**:
```python
try:
    roles = Role.get_role_by_department_id(department_id=1)
    for role in roles:
        print(f"角色: {role['name']}, 权限数量: {len(role['permissions'])}")
except RoleModelException as e:
    print(f"获取失败: {e.message}")
```

## 权限管理

### 权限存储格式

角色的权限以字符串列表的形式存储在 `permissions` 字段中：

```python
permissions = [
    "user.create",
    "user.read", 
    "user.update",
    "department.read",
    "role.create"
]
```

### 权限验证示例

```python
def check_role_permission(role_id: int, required_permission: str) -> bool:
    """检查角色是否具有指定权限"""
    try:
        role = Role.get_role(role_id)
        return required_permission in role['permissions']
    except RoleModelException:
        return False

# 使用示例
if check_role_permission(1, "user.create"):
    print("角色具有创建用户权限")
else:
    print("角色没有创建用户权限")
```

### 权限继承设计

可以实现基于部门层级的权限继承：

```python
def get_inherited_permissions(role_id: int) -> List[str]:
    """获取角色的继承权限（包含上级部门角色权限）"""
    try:
        role = Role.get_role(role_id)
        permissions = set(role['permissions'])
        
        # 获取部门信息
        from models.core.department import Department
        department = Department.get_department(role['department_id'])
        
        # 如果有父部门，获取父部门的角色权限
        if department['parent_id']:
            parent_roles = Role.get_role_by_department_id(department['parent_id'])
            for parent_role in parent_roles:
                permissions.update(parent_role['permissions'])
        
        return list(permissions)
    except Exception:
        return []
```

## 使用场景

### 1. 角色权限管理

```python
def assign_permissions_to_role(role_id: int, new_permissions: List[str]):
    """为角色分配权限"""
    try:
        # 获取当前角色信息
        role = Role.get_role(role_id)
        
        # 合并权限（去重）
        current_permissions = set(role['permissions'])
        current_permissions.update(new_permissions)
        
        # 更新角色权限
        result = Role.update(role_id, permissions=list(current_permissions))
        return result
    except RoleModelException as e:
        print(f"权限分配失败: {e.message}")
        return None
```

### 2. 角色模板创建

```python
def create_role_template(department_id: int, role_type: str):
    """根据角色类型创建角色模板"""
    role_templates = {
        "admin": {
            "name": "管理员",
            "description": "部门管理员角色",
            "permissions": [
                "user.create", "user.read", "user.update", "user.delete",
                "department.read", "role.create", "role.read", "role.update"
            ]
        },
        "operator": {
            "name": "操作员", 
            "description": "普通操作员角色",
            "permissions": [
                "user.read", "department.read", "role.read"
            ]
        },
        "viewer": {
            "name": "查看者",
            "description": "只读权限角色", 
            "permissions": [
                "user.read", "department.read"
            ]
        }
    }
    
    if role_type in role_templates:
        template = role_templates[role_type]
        return Role.create(
            name=template["name"],
            department_id=department_id,
            description=template["description"],
            permissions=template["permissions"]
        )
    else:
        raise ValueError("不支持的角色类型")
```

### 3. 批量角色操作

```python
def batch_update_role_permissions(role_ids: List[int], permissions: List[str]):
    """批量更新角色权限"""
    results = []
    for role_id in role_ids:
        try:
            result = Role.update(role_id, permissions=permissions)
            results.append({"role_id": role_id, "status": "success"})
        except RoleModelException as e:
            results.append({"role_id": role_id, "status": "failed", "error": e.message})
    return results
```

## 注意事项

### 1. 数据完整性
- 创建角色时必须指定有效的部门ID
- 删除角色前应检查是否有用户关联该角色
- 权限列表应该包含有效的权限代码

### 2. 权限验证
- 权限代码应该与 PermissionManager 中注册的权限一致
- 建议在分配权限前验证权限的有效性
- 避免分配过多不必要的权限

### 3. 性能考虑
- 权限列表存储为JSON格式，查询时需要反序列化
- 对于频繁的权限检查，建议使用缓存机制
- 避免在权限列表中存储过多权限

### 4. 安全性
- 敏感权限的分配应该有审批流程
- 定期审查角色权限，移除不必要的权限
- 记录权限变更日志

### 5. 事务管理
- 所有数据库操作都在事务中执行
- 发生异常时会自动回滚事务
- 确保数据一致性

## 最佳实践

1. **角色设计**: 按照最小权限原则设计角色
2. **权限分组**: 将相关权限组织成逻辑组
3. **角色继承**: 考虑实现基于部门的角色继承
4. **权限审计**: 定期审查和清理不必要的权限
5. **异常处理**: 始终使用 try-catch 块处理可能的异常
6. **数据验证**: 在分配权限前验证权限的有效性 