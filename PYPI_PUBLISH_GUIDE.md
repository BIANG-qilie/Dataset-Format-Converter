# PyPI发布指南

## 🚀 将 labelimgobb2DOTA-converter 发布到 PyPI

### 1. 前置准备

#### 安装发布工具
```bash
pip install build twine
```

#### 注册账号
1. **TestPyPI（测试环境）**：https://test.pypi.org/account/register/
2. **PyPI（正式环境）**：https://pypi.org/account/register/

#### 生成API令牌
1. 登录 PyPI → Account Settings → API tokens
2. 创建新令牌，选择 "Entire account" 范围
3. 复制生成的令牌（格式：`pypi-xxxxxxxx`）

### 2. 构建包

```bash
# 清理之前的构建
Remove-Item -Recurse -Force dist, build, *.egg-info -ErrorAction SilentlyContinue

# 构建包
python -m build

# 检查包的质量
python -m twine check dist/*
```

### 3. 测试发布（推荐）

```bash
# 上传到 TestPyPI
python -m twine upload --repository testpypi dist/*
# 输入用户名: __token__
# 输入密码: 你的TestPyPI API令牌

# 测试安装
pip install --index-url https://test.pypi.org/simple/ labelimgobb2DOTA-converter

# 测试功能
labelimgobb2DOTA-cli --help
labelimgobb2DOTA-gui
```

### 4. 正式发布

```bash
# 上传到 PyPI
python -m twine upload dist/*
# 输入用户名: __token__
# 输入密码: 你的PyPI API令牌
```

### 5. 验证发布

```bash
# 安装验证
pip install labelimgobb2DOTA-converter

# 功能测试
labelimgobb2DOTA-cli --help
python -c "from yoloobb_converter import YOLOOBB2labelimgOBB; print('导入成功')"
```

### 6. 配置文件方式（可选）

创建 `~/.pypirc` 文件：
```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-你的API令牌

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-你的测试API令牌
```

配置后可以直接使用：
```bash
python -m twine upload --repository testpypi dist/*  # 测试环境
python -m twine upload dist/*                        # 正式环境
```

### 7. 版本更新流程

1. **更新版本号**：修改 `yoloobb_converter/__init__.py` 中的 `__version__`
2. **更新日志**：在 `README.md` 中记录变更
3. **重新构建**：`python -m build`
4. **发布新版本**：`python -m twine upload dist/*`

### 8. 常见问题

#### 包名冲突
如果包名 `labelimgobb2DOTA-converter` 已被占用，可以：
1. 修改 `pyproject.toml` 中的 `name` 字段
2. 选择新的包名，如：`yolo-obb-converter`、`obb-converter` 等

#### 许可证警告
目前配置中有许可证格式警告，可以忽略，不影响发布。

#### 依赖问题
确保所有依赖都在 `pyproject.toml` 中正确声明。

### 9. 发布检查清单

- [ ] 包构建成功
- [ ] `twine check` 通过
- [ ] 在 TestPyPI 测试成功
- [ ] CLI 和 GUI 功能正常
- [ ] README 文档完整
- [ ] 版本号正确
- [ ] 许可证文件存在

### 10. 发布后

发布成功后，用户可以通过以下方式安装：

```bash
pip install labelimgobb2DOTA-converter
```

并使用：
```bash
labelimgobb2DOTA-cli    # 命令行工具
labelimgobb2DOTA-gui    # 图形界面
```

或在Python代码中：
```python
from yoloobb_converter import YOLOOBB2labelimgOBB, labelimgOBB2YOLOOBB
``` 