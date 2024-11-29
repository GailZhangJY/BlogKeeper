# BlogKeeper

BlogKeeper 是一个专业的博客内容管理工具，致力于帮助用户保存、转换和管理来自各大博客平台的文章内容。无论是备份珍贵的博客文章，还是转换文章格式以便二次创作，BlogKeeper 都能满足您的需求。

## ✨ 核心特性

- 🌐 **多平台支持**
  - 支持主流博客平台
  - 智能识别文章结构
  - 自动提取文章元数据

- 📦 **多格式导出**
  - HTML（保留原始样式）
  - PDF（适合归档打印）
  - Markdown（便于编辑）
  - MHTML（单文件保存）

- 🎨 **样式完整性**
  - 保留原文排版
  - 自动处理图片资源
  - 保持CSS样式

- 🛠️ **高级功能**
  - 批量文章处理
  - 智能错误恢复
  - 灵活的保存选项

## 🚀 快速开始

### 安装

```bash
pip install -r requirements.txt
```

### 基本使用

```python
from base_parser import BlogParser

# 创建解析器实例
parser = BlogParser()

# 下载单篇文章
parser.parse(
    url="https://example.com/blog/post",
    save_options={'formats': ['html', 'pdf', 'markdown', 'mhtml']}
)
```

## 📚 支持的格式

| 格式 | 特点 | 适用场景 |
|------|------|----------|
| HTML | 完整保留原文样式 | 离线浏览 |
| PDF | 保真度高，布局固定 | 存档、打印 |
| Markdown | 纯文本，易于编辑 | 内容编辑 |
| MHTML | 单文件，资源集成 | 完整备份 |

## 🔧 配置选项

```python
save_options = {
    'formats': ['html', 'pdf', 'markdown', 'mhtml],  # 保存格式
    'output_dir': './blogs',                 # 输出目录
    'debug': False                           # 调试模式
}
```

## 📝 许可证

MIT License

## 🤝 贡献

欢迎提交问题和改进建议！
