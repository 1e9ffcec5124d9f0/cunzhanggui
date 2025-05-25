# Permission 权限模型文档

## 概述

`PermissionManager` 是一个权限管理器类，用于管理系统中的权限注册和查询。该类采用类方法设计，提供了权限的注册和获取功能，是系统权限控制的核心组件。

## 设计特点

- **单例模式**: 使用类级别的私有字典存储权限信息
- **简单高效**: 基于内存的权限存储，查询速度快
- **类方法设计**: 无需实例化即可使用
- **键值对存储**: 权限键和权限名称的映射关系

## 异常处理

### PermissionModelException

自定义异常类，用于处理权限相关的异常情况。

**属性**:
- `code`: 错误代码
- `message`: 错误信息

**构造函数**:
```python
def __init__(self, code: int, message: str)
```

## 类结构

### 私有属性

- `__permissions`: 类级别的私有字典，存储所有注册的权限信息
  - 键: `permission_key` (权限代码)
  - 值: `permission_name` (权限名称)

## 方法详解

### 1. register_permission() - 注册权限

```python
@classmethod
def register_permission(cls, permission_key: str, permission_name: str) -> None
```

**功能**: 向系统注册新的权限

**参数**:
- `permission_key` (str): 权限键/权限代码，用作唯一标识符
- `permission_name` (str): 权限名称，用于显示和描述

**返回值**: 
- `None`: 无返回值

**特点**:
- 如果权限键已存在，会覆盖原有的权限名称
- 权限键应该具有唯一性和描述性
- 建议使用模块化的命名规范

**使用示例**:
```python
# 注册用户管理相关权限
PermissionManager.register_permission("user.create", "创建用户")
PermissionManager.register_permission("user.read", "查看用户")
PermissionManager.register_permission("user.update", "更新用户")
PermissionManager.register_permission("user.delete", "删除用户")

# 注册部门管理相关权限
PermissionManager.register_permission("department.create", "创建部门")
PermissionManager.register_permission("department.read", "查看部门")
PermissionManager.register_permission("department.update", "更新部门")
PermissionManager.register_permission("department.delete", "删除部门")

# 注册角色管理相关权限
PermissionManager.register_permission("role.create", "创建角色")
PermissionManager.register_permission("role.read", "查看角色")
PermissionManager.register_permission("role.update", "更新角色")
PermissionManager.register_permission("role.delete", "删除角色")
```

### 2. get_all_permissions() - 获取所有权限

```python
@classmethod
def get_all_permissions(cls) -> Dict[str, str]
```

**功能**: 获取系统中所有已注册的权限

**参数**: 无

**返回值**: 
- `Dict[str, str]`: 包含所有权限的字典
  - 键: 权限代码
  - 值: 权限名称

**使用示例**:
```python
# 获取所有权限
all_permissions = PermissionManager.get_all_permissions()

# 打印所有权限
for permission_key, permission_name in all_permissions.items():
    print(f"权限代码: {permission_key}, 权限名称: {permission_name}")

# 检查特定权限是否存在
if "user.create" in all_permissions:
    print(f"用户创建权限: {all_permissions['user.create']}")

# 获取权限总数
permission_count = len(all_permissions)
print(f"系统共有 {permission_count} 个权限")
```

## 权限命名规范

### 建议的命名格式

采用 `模块.操作` 的格式，便于管理和理解：

```python
# 用户管理模块
"user.create"     # 创建用户
"user.read"       # 查看用户
"user.update"     # 更新用户
"user.delete"     # 删除用户
"user.list"       # 用户列表

# 部门管理模块
"department.create"   # 创建部门
"department.read"     # 查看部门
"department.update"   # 更新部门
"department.delete"   # 删除部门
"department.tree"     # 部门树查看



```

### 权限层级设计

可以设计多层级的权限结构：

```python
# 一级权限 - 模块级别
"user"            # 用户模块访问权限
"department"      # 部门模块访问权限
"role"            # 角色模块访问权限

# 二级权限 - 操作级别
"user.manage"     # 用户管理权限
"user.view"       # 用户查看权限

# 三级权限 - 具体操作
"user.manage.create"  # 创建用户权限
"user.manage.delete"  # 删除用户权限
```


## 注意事项

### 1. 内存存储
- 权限信息存储在内存中，应用重启后需要重新注册
- 建议在应用启动时统一注册所有权限
- 不适合存储大量权限信息

### 2. 线程安全
- 当前实现未考虑线程安全问题
- 在多线程环境中可能需要添加锁机制
- 建议在应用启动阶段完成权限注册

### 3. 权限持久化
- 当前版本不支持权限的持久化存储
- 如需持久化，建议结合数据库实现
- 可以考虑将权限信息存储到配置文件

### 4. 权限验证
- PermissionManager 只负责权限的注册和查询
- 具体的权限验证逻辑需要在业务层实现
- 建议结合装饰器模式实现权限验证

## 扩展建议

### 1. 权限分组

```python
@classmethod
def register_permission_group(cls, group_name: str, permissions: Dict[str, str]) -> None:
    """批量注册权限组"""
    for key, name in permissions.items():
        full_key = f"{group_name}.{key}"
        cls.register_permission(full_key, name)
```

### 2. 权限搜索

```python
@classmethod
def search_permissions(cls, keyword: str) -> Dict[str, str]:
    """根据关键词搜索权限"""
    result = {}
    for key, name in cls.__permissions.items():
        if keyword in key or keyword in name:
            result[key] = name
    return result
```

### 3. 权限导出

```python
@classmethod
def export_permissions(cls) -> str:
    """导出权限配置为JSON格式"""
    import json
    return json.dumps(cls.__permissions, ensure_ascii=False, indent=2)
```

## 最佳实践

1. **统一注册**: 在应用启动时统一注册所有权限
2. **命名规范**: 使用一致的权限命名规范
3. **分类管理**: 按模块或功能对权限进行分类
4. **文档维护**: 维护权限清单文档
5. **版本控制**: 对权限变更进行版本控制 