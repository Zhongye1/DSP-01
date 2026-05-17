## 数据结构习题集整理：

使用 `pdflatex` 命令将.tex文件编译为PDF文档：

```
pdflatex 数据结构2009-题库.tex
```

### 2. 使用LaTeX编辑器

- TeXstudio
- TeXmaker
- Overleaf（在线编辑器）
- WinEdt
- VSCode配合LaTeX Workshop插件

### 转换为Word文档

```bash
pandoc 数据结构2009-题库.tex -o 数据结构2009-题库.docx
```

或使用脚本

```bash
python convert_latex_to_word.py
```
