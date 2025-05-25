# Department Services 部门服务层文档

## 概述

`department_services.py` 是部门管理的服务层模块，提供了部门的创建、更新、删除、查询等核心业务功能。该模块基于权限控制，所有操作都需要相应的权限验证，并且遵循部门层级管理规则。

## 技术栈

- **权限控制**: 基于 `PermissionManager` 和 `@require_permission` 装饰器
- **数据模型**: 使用 `Department` 模型进行数据操作
- **异常处理**: 自定义 `DepartmentServiceException` 异常类
- **调试模式**: 支持 `DEBUG_MODE` 配置的错误信息显示

## 异常处理

### DepartmentServiceException

部门服务层自定义异常类，用于处理业务逻辑相关的异常情况。

**属性**:
- `code` (int): 错误代码
- `message` (str): 错误信息

**构造函数**:
```python
def __init__(self, code: int, message: str)
```

**常见错误代码**:
- `400`: 业务逻辑错误（如权限不足、层级限制等）
- `500`: 系统内部错误

## 权限注册

模块在加载时自动注册以下权限：

| 权限代码 | 权限名称 | 描述 |
|---------|---------|------|
| `department.manage.create` | 创建部门权限 | 允许创建子部门 |
| `department.manage.update` | 更新部门权限 | 允许更新子部门信息 |
| `department.manage.delete` | 删除部门权限 | 允许删除子部门 |
| `department.view.get` | 获取部门权限 | 允许查看部门信息 |
| `department.view.tree` | 获取部门树权限 | 允许查看部门树结构 |

## 服务函数详解

### 1. create_department() - 创建子部门

```python
@require_permission("department.manage.create")
def create_department(current_user: User, name: str, description: Optional[str] = None,
                     manager_name: Optional[str] = None, manager_phone: Optional[str] = None) -> Dict[str, str]
```

**功能**: 为当前用户所在部门创建直接子部门

**权限要求**: `department.manage.create`

**参数**:
- `current_user` (User): 当前操作用户对象，必填
- `name` (str): 部门名称，必填
- `description` (Optional[str]): 部门描述信息，可选
- `manager_name` (Optional[str]): 部门负责人姓名，可选
- `manager_phone` (Optional[str]): 部门负责人联系电话，可选

**返回值**: 
- 成功: `{'success': "部门创建成功"}`

**异常**:
- `DepartmentServiceException`: 
  - 400: 村社级部门不能再创建子部门
  - 500: 创建部门失败
- `PermissionServiceException`: 权限验证失败

**业务规则**:
- 只能创建当前部门的直接子部门
- 新部门的级别为当前部门级别+1
- 村社级部门（level=3）不能再创建子部门
- 新部门的父部门ID为当前用户所在部门ID

**使用示例**:
```python
try:
    result = create_department(
        current_user=current_user,
        name="技术开发科",
        description="负责系统技术开发工作",
        manager_name="张三",
        manager_phone="13800138000"
    )
    print(result)  # {'success': '部门创建成功'}
except DepartmentServiceException as e:
    print(f"创建失败: {e.message}")
except PermissionServiceException as e:
    print(f"权限不足: {e.message}")
```

### 2. update_department() - 更新部门信息

```python
@require_permission("department.manage.update")
def update_department(current_user: User, department_id: int, name: Optional[str] = None,
                     description: Optional[str] = None, manager_name: Optional[str] = None,
                     manager_phone: Optional[str] = None) -> Dict[str, str]
```

**功能**: 更新指定子部门的信息

**权限要求**: `department.manage.update`

**参数**:
- `current_user` (User): 当前操作用户对象，必填
- `department_id` (int): 要更新的子部门ID，必填
- `name` (Optional[str]): 部门名称，可选
- `description` (Optional[str]): 部门描述信息，可选
- `manager_name` (Optional[str]): 部门负责人姓名，可选
- `manager_phone` (Optional[str]): 部门负责人联系电话，可选

**返回值**: 
- 成功: `{'success': "部门更新成功"}`

**异常**:
- `DepartmentServiceException`: 
  - 400: 只能更新直接子部门
  - 500: 更新部门失败
- `PermissionServiceException`: 权限验证失败

**业务规则**:
- 只能更新当前部门的直接子部门
- 不能更新非直接下级的部门
- 只更新传入的非空参数

**使用示例**:
```python
try:
    result = update_department(
        current_user=current_user,
        department_id=5,
        name="技术研发科",
        manager_name="李四"
    )
    print(result)  # {'success': '部门更新成功'}
except DepartmentServiceException as e:
    print(f"更新失败: {e.message}")
```

### 3. delete_department() - 删除部门

```python
@require_permission('department.manage.delete')
def delete_department(current_user: User, department_id: int) -> Dict[str, str]
```

**功能**: 删除指定的子部门

**权限要求**: `department.manage.delete`

**参数**:
- `current_user` (User): 当前操作用户对象，必填
- `department_id` (int): 要删除的子部门ID，必填

**返回值**: 
- 成功: `{'success': "部门删除成功"}`

**异常**:
- `DepartmentServiceException`: 
  - 400: 只能删除直接子部门
  - 500: 删除部门失败
- `PermissionServiceException`: 权限验证失败

**业务规则**:
- 只能删除当前部门的直接子部门
- 不能删除非直接下级的部门
- 删除操作不可逆，需谨慎使用

**注意事项**:
- 删除前应确保该部门下没有用户
- 删除前应确保该部门没有子部门
- 建议在删除前进行确认操作

**使用示例**:
```python
try:
    result = delete_department(
        current_user=current_user,
        department_id=5
    )
    print(result)  # {'success': '部门删除成功'}
except DepartmentServiceException as e:
    print(f"删除失败: {e.message}")
```

### 4. get_department() - 获取部门信息

```python
@require_permission('department.view.get')
def get_department(current_user: User, department_id: Optional[int] = None) -> Department
```

**功能**: 获取部门详细信息

**权限要求**: `department.view.get`

**参数**:
- `current_user` (User): 当前操作用户对象，必填
- `department_id` (Optional[int]): 部门ID，可选

**返回值**: 
- `Department`: 部门对象，包含完整的部门信息

**异常**:
- `DepartmentServiceException`: 
  - 400: 只能获取当前部门或子部门(包括子部门的子部门)
  - 500: 获取部门失败
- `PermissionServiceException`: 权限验证失败

**业务规则**:
- 如果不提供 `department_id`，返回当前用户所在部门
- 如果提供 `department_id`，只能获取当前部门或其子部门（包括子部门的子部门）
- 不能获取平级部门或上级部门的信息

**使用示例**:
```python
try:
    # 获取当前用户所在部门
    current_dept = get_department(current_user=current_user)
    print(f"当前部门: {current_dept.name}")
    
    # 获取指定子部门
    sub_dept = get_department(current_user=current_user, department_id=5)
    print(f"子部门: {sub_dept.name}")
except DepartmentServiceException as e:
    print(f"获取失败: {e.message}")
```

### 5. get_department_tree() - 获取部门树

```python
@require_permission('department.view.tree')
def get_department_tree(current_user: User) -> List[Dict[str, str]]
```

**功能**: 获取以当前部门为根的完整部门树结构

**权限要求**: `department.view.tree`

**参数**:
- `current_user` (User): 当前操作用户对象，必填

**返回值**: 
- `List[Dict[str, str]]`: 部门树列表，每个部门包含 `children` 字段

**异常**:
- `DepartmentServiceException`: 
  - 500: 获取部门树失败
- `PermissionServiceException`: 权限验证失败

**业务规则**:
- 以当前用户所在部门为根节点
- 递归获取所有子部门
- 返回完整的树形结构

**数据结构示例**:
```python
[
    {
        "id": 1,
        "name": "技术部",
        "level": 1,
        "parent_id": 0,
        "description": "技术开发部门",
        "manager_name": "张三",
        "manager_phone": "13800138000",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "children": [
            {
                "id": 2,
                "name": "前端组",
                "level": 2,
                "parent_id": 1,
                "children": []
            },
            {
                "id": 3,
                "name": "后端组", 
                "level": 2,
                "parent_id": 1,
                "children": []
            }
        ]
    }
]
```

**使用示例**:
```python
try:
    tree = get_department_tree(current_user=current_user)
    
    def print_tree(departments, indent=0):
        for dept in departments:
            print("  " * indent + f"- {dept['name']} (级别: {dept['level']})")
            if dept.get('children'):
                print_tree(dept['children'], indent + 1)
    
    print("部门树结构:")
    print_tree(tree)
except DepartmentServiceException as e:
    print(f"获取部门树失败: {e.message}")
```

## 权限控制机制

### 权限装饰器

所有服务函数都使用 `@require_permission` 装饰器进行权限验证：

```python
@require_permission("department.manage.create")
def create_department(current_user: User, ...):
    # 函数体
```

### 权限验证流程

1. **装饰器拦截**: `@require_permission` 装饰器首先拦截函数调用
2. **用户权限检查**: 验证 `current_user` 是否具有所需权限
3. **权限验证**: 通过 `PermissionServiceException` 抛出权限相关异常
4. **业务逻辑执行**: 权限验证通过后执行具体业务逻辑

### 权限分配建议

| 角色类型 | 建议权限 | 说明 |
|---------|---------|------|
| 部门管理员 | 所有 department 权限 | 可以管理本部门及子部门 |
| 部门主管 | `department.view.*`, `department.manage.update` | 可以查看和更新部门信息 |
| 普通用户 | `department.view.get` | 只能查看部门基本信息 |
| 系统管理员 | 所有权限 | 超级管理员权限 |

## 业务规则说明

### 部门层级限制

系统支持4级部门结构：
- **0级**: 根部门（总部）
- **1级**: 县级部门
- **2级**: 镇街级部门
- **3级**: 村社级部门（最底层，不能再创建子部门）

### 操作权限范围

1. **创建部门**: 只能在当前部门下创建直接子部门
2. **更新部门**: 只能更新直接子部门的信息
3. **删除部门**: 只能删除直接子部门
4. **查看部门**: 可以查看当前部门及所有子部门（包括子部门的子部门）

### 数据访问控制

- 用户只能操作自己所在部门及其子部门
- 不能跨部门操作（除非有特殊权限）
- 不能操作上级部门或平级部门

## 错误处理策略

### 异常层级

1. **权限异常**: `PermissionServiceException` - 权限验证失败
2. **业务异常**: `DepartmentServiceException` - 业务逻辑错误
3. **模型异常**: `DepartmentModelException` - 数据层错误

### 错误信息处理

```python
try:
    # 业务逻辑
    pass
except DepartmentModelException as e:
    # 将模型异常转换为服务异常
    raise DepartmentServiceException(code=e.code, message=e.message)
except PermissionServiceException as e:
    # 权限异常直接抛出
    raise e
except Exception as e:
    # 其他异常根据调试模式处理
    if DEBUG_MODE:
        raise DepartmentServiceException(code=500, message=f"操作失败: {e}")
    else:
        raise DepartmentServiceException(code=500, message="操作失败")
```

### 调试模式

- **DEBUG_MODE=True**: 显示详细错误信息，包含异常堆栈
- **DEBUG_MODE=False**: 只显示用户友好的错误信息，隐藏技术细节

## 使用场景示例

### 1. 部门管理员创建子部门

```python
def admin_create_department(admin_user, dept_info):
    """管理员创建部门的完整流程"""
    try:
        # 验证输入数据
        if not dept_info.get('name'):
            return {"error": "部门名称不能为空"}
        
        # 创建部门
        result = create_department(
            current_user=admin_user,
            name=dept_info['name'],
            description=dept_info.get('description', ''),
            manager_name=dept_info.get('manager_name'),
            manager_phone=dept_info.get('manager_phone')
        )
        
        return {"success": True, "message": "部门创建成功"}
    except DepartmentServiceException as e:
        return {"error": e.message}
    except PermissionServiceException as e:
        return {"error": "权限不足"}
```

### 2. 获取部门组织架构

```python
def get_organization_structure(user):
    """获取用户可见的组织架构"""
    try:
        # 获取部门树
        tree = get_department_tree(current_user=user)
        
        # 格式化为前端需要的格式
        def format_tree(departments):
            result = []
            for dept in departments:
                formatted = {
                    "id": dept['id'],
                    "label": dept['name'],
                    "level": dept['level'],
                    "manager": dept.get('manager_name', ''),
                    "children": format_tree(dept.get('children', []))
                }
                result.append(formatted)
            return result
        
        return {
            "success": True,
            "data": format_tree(tree)
        }
    except Exception as e:
        return {"error": "获取组织架构失败"}
```

### 3. 批量部门操作

```python
def batch_update_departments(user, updates):
    """批量更新部门信息"""
    results = []
    
    for update in updates:
        try:
            result = update_department(
                current_user=user,
                department_id=update['id'],
                name=update.get('name'),
                description=update.get('description'),
                manager_name=update.get('manager_name'),
                manager_phone=update.get('manager_phone')
            )
            results.append({
                "id": update['id'],
                "status": "success",
                "message": "更新成功"
            })
        except Exception as e:
            results.append({
                "id": update['id'],
                "status": "failed",
                "message": str(e)
            })
    
    return results
```

## 最佳实践

### 1. 权限设计
- 遵循最小权限原则
- 按职责分配权限
- 定期审查权限分配

### 2. 异常处理
- 始终使用 try-catch 块
- 区分不同类型的异常
- 提供用户友好的错误信息

### 3. 业务逻辑
- 在服务层进行业务规则验证
- 保持服务函数的单一职责
- 避免在服务层直接操作数据库

### 4. 安全考虑
- 验证用户输入
- 检查操作权限
- 记录敏感操作日志

### 5. 性能优化
- 避免不必要的数据库查询
- 使用缓存机制
- 合理设计数据结构

## 注意事项

1. **权限验证**: 所有操作都需要相应权限，确保用户具有必要权限
2. **层级限制**: 注意部门层级限制，村社级部门不能再创建子部门
3. **数据完整性**: 删除部门前确保没有关联数据
4. **异常处理**: 正确处理各种异常情况，提供友好的错误信息
5. **调试模式**: 生产环境应关闭调试模式，避免泄露敏感信息 