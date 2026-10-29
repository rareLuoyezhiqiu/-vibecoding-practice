# vibecoding-practice

用 AI 辅助编程（vibe coding）练习的小项目。

## 项目

### `todo/` — 网页版待办清单

原生 HTML/CSS/JS，无任何依赖，数据保存在浏览器 `localStorage`。

双击 `todo/index.html` 即可使用。

### `todo-desktop/` — 桌面版待办清单

Python + Tkinter 写的 Windows 桌面程序，不依赖浏览器、不占端口。数据保存在
`%USERPROFILE%\.vibecoding_todos.json`（卸载时不会删除）。

功能：添加、标记完成、删除、筛选（全部/未完成/已完成）、清除已完成、自动保存。

直接运行源码：

```bash
python todo_app.py
```

打包成单个 exe：

```bash
python -m pip install pyinstaller
python -m PyInstaller --noconfirm --clean --onefile --windowed --icon icon.ico --name TodoList todo_app.py
```

生成安装包（需要 [Inno Setup 6](https://jrsoftware.org/isinfo.php)）：

```bash
ISCC.exe installer.iss
```

`dist/`、`build/`、`installer/`、`*.spec` 等构建产物不提交到仓库。
