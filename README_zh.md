# QOC (Quanta of Code) - 代码贡献量测量工具

基于抽象语法树（AST）的代码贡献量度量工具，提供比传统代码行数更准确的代码评估。

## 什么是QOC？

QOC（Quanta of Code，代码贡献量）是一种基于抽象语法树（AST）分析的代码贡献度量指标。它通过为不同语法元素分配权重来量化有意义代码的实际贡献，过滤掉格式化噪音并专注于实质性的代码贡献。相比传统的代码行数（LOC）统计具有以下优势：

- **衡量实际代码贡献量**：忽略空行、注释、代码格式等非贡献性元素
- **反映真实编程工作量**：基于语法结构而非简单行数统计
- **语言无关性**：统一的度量标准适用于不同编程语言

## 核心理念

传统的代码行数（LOC）指标存在以下问题：

1. **容易被编程习惯干扰**：换行、空行、注释等不影响实际代码贡献
2. **无法区分代码贡献量**：简单赋值和复杂算法在行数上可能相同
3. **不擅长检测重构**：代码块移动会产生大量虚假变更

QOC通过以下方式解决这些问题：
- 解析源代码为抽象语法树（AST）
- 为不同类型的AST节点基于其代码贡献分配权重
- 计算加权总和作为总代码贡献量（QOC值）

## 支持的编程语言

### 🟢 完全支持（基于Tree-sitter AST分析）

| 语言 | 文件扩展名 | AST解析器 | 权重配置 |
|------|-----------|-----------|----------|
| **Python** | `.py` | ✅ Python + Tree-sitter | ✅ 完整 |
| **JavaScript/TypeScript** | `.js`, `.jsx`, `.ts`, `.tsx` | ✅ Tree-sitter | ✅ 完整 |
| **Java** | `.java` | ✅ Tree-sitter | ✅ 完整 |
| **C++** | `.cpp`, `.cc`, `.cxx`, `.hpp`, `.hxx`, `.h` | ✅ Tree-sitter | ✅ 完整 |

## 功能特性

- ✅ **多语言AST分析** - 支持Python、JavaScript、Java、C++等
- ✅ **基于Tree-sitter** - 高性能、准确的语法解析
- ✅ **智能权重系统** - 可配置的节点权重，反映代码贡献量
- ✅ **多种分析模式** - 单文件、目录批量分析
- ✅ **详细统计报告** - AST节点统计、权重贡献分析
- ✅ **多输出格式** - 控制台美化输出、JSON、CSV
- ✅ **文件对比功能** - 比较两个文件的代码贡献量差异
- ✅ **语言分布统计** - 多语言项目的统计分析

## 安装

### 1. 克隆仓库
```bash
git clone https://github.com/ufoym/qoc
cd qoc
```

### 2. 创建虚拟环境
```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

## 使用方法

### 快速体验
```bash
python -m qoc demo
```

### 分析单个文件
```bash
# 基本分析
python -m qoc analyze file.py

# 详细分析（显示AST节点统计）
python -m qoc analyze file.java -d

# 多语言支持
python -m qoc analyze Calculator.java -d
python -m qoc analyze main.cpp -d
python -m qoc analyze app.js -d
```

### 分析整个项目
```bash
# 分析当前目录
python -m qoc analyze .

# 递归分析所有子目录
python -m qoc analyze ./src --recursive

# 分析多语言项目
python -m qoc analyze . -r  # 自动识别所有支持的语言
```

### 文件比较
```bash
python -m qoc compare old_version.py new_version.py
```

### 不同输出格式
```bash
# JSON格式输出
python -m qoc analyze file.py --format json

# CSV格式输出
python -m qoc analyze . -r --format csv

# 保存到文件
python -m qoc analyze . -r -o report.json --format json
```

## 实际应用示例

### 不同语言的QOC对比

```bash
# Java类：33行代码 → 363.0 QOC（比率：11.00）
python -m qoc analyze Calculator.java

# JavaScript类：43行代码 → 561.5 QOC（比率：13.06）
python -m qoc analyze Calculator.js

# C++类：59行代码 → 885.0 QOC（比率：15.00）
python -m qoc analyze Calculator.cpp
```

### 大规模项目分析
```bash
# 分析整个项目（示例输出）
python -m qoc analyze . -r

总文件数: 931
总代码贡献量: 2,325,852.4
总代码行数: 251,546
平均效率比率: 9.25

语言分布：
- Python: 922 文件 (99.9%)
- JavaScript: 1 文件 (0.0%)
- Java: 1 文件 (0.0%) 
- C++: 1 文件 (0.0%)
```

## 权重配置说明

工具使用`config.json`配置不同AST节点的权重：

```json
{
  "languages": {
    "python": {
      "node_weights": {
        "function_definition": 10,    // 函数定义权重高
        "class_definition": 15,       // 类定义权重最高
        "if_statement": 3,            // 条件语句中等权重
        "for_statement": 4,           // 循环语句中等权重
        "identifier": 0.5,            // 标识符权重低
        ...
      }
    }
  }
}
```

## 项目结构

```
qoc/
├── src/
│   └── qoc/
│       ├── __init__.py          # 包初始化
│       ├── __main__.py          # 命令行入口
│       ├── models.py            # 数据模型
│       ├── analyzer.py          # 核心分析器
│       └── cli.py               # 命令行界面
├── config.json                  # 配置文件
├── requirements.txt             # Python依赖
└── README.md                    # 项目说明
```

## 技术实现

### AST解析技术栈
- **Tree-sitter**: 高性能增量解析库
- **多语言支持**: 各语言专用解析器
- **统一API**: 一致的节点访问接口

### 权重计算算法
1. **解析阶段**: 将源代码解析为AST
2. **遍历阶段**: 深度优先遍历所有节点
3. **权重映射**: 根据各节点对代码贡献量的配置计算权重
4. **累加计算**: 计算总代码贡献量（QOC值）

## 与传统LOC的对比

| 指标 | 传统LOC | QOC |
|------|---------|------------|
| **代码风格独立性** | ❌ 受格式影响 | ✅ 忽略格式化 |
| **代码贡献量测量** | ❌ 简单行数统计 | ✅ 基于实际代码贡献加权 |
| **语言一致性** | ❌ 各语言标准不同 | ✅ 统一测量标准 |
| **重构检测** | ❌ 高虚假阳性率 | ✅ 专注实际代码变更 |
| **测量准确性** | ❌ 容易被欺骗 | ✅ 反映真实代码贡献量 |

## 开发指南

### 开发环境设置
```bash
git clone https://github.com/ufoym/qoc
cd qoc
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 运行测试
```bash
python -m pytest tests/
```

### 添加新语言支持
1. 在 `config.json` 中添加语言配置
2. 更新 `analyzer.py` 中的解析器初始化
3. 添加对应的tree-sitter语言包

## 贡献指南

欢迎贡献代码和建议！请遵循以下步骤：

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)  
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 更新日志

### v0.1.0
- 🎉 初始版本发布
- ✅ 支持Python、JavaScript、Java、C++
- ✅ 基于Tree-sitter的AST分析
- ✅ 多种输出格式（Console、JSON、CSV）
- ✅ 文件对比功能
- ✅ 模块化架构设计 