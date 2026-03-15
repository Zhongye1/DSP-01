import os
import subprocess
import sys
from pathlib import Path

def install_pypandoc():
    """尝试安装pypandoc"""
    try:
        import pypandoc
        return True
    except ImportError:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pypandoc"])
            import pypandoc
            return True
        except Exception as e:
            print(f"无法安装pypandoc: {e}")
            return False

def convert_latex_to_docx(latex_file_path):
    """使用pypandoc将LaTeX转换为Word文档"""
    try:
        import pypandoc
        docx_file = latex_file_path.replace('.tex', '.docx')
        
        # 尝试转换
        output = pypandoc.convert_file(latex_file_path, 'docx', outputfile=docx_file)
        
        if os.path.exists(docx_file):
            print(f"成功转换: {latex_file_path} -> {docx_file}")
            return docx_file
        else:
            print("转换可能未成功，输出文件不存在")
            return None
            
    except ImportError:
        print("pypandoc未安装或不可用")
        return None
    except Exception as e:
        print(f"转换过程中出错: {e}")
        return None

def main():
    # 获取当前目录下的LaTeX文件
    current_dir = Path('.')
    latex_files = list(current_dir.glob('*.tex'))
    
    print(f"在当前目录找到 {len(latex_files)} 个LaTeX文件:")
    for i, lf in enumerate(latex_files):
        print(f"{i+1}. {lf.name}")
    
    if not latex_files:
        print("没有找到LaTeX文件")
        return
    
    # 转换数据结构2009题库
    target_file = "数据结构2009-题库.tex"
    if target_file in [f.name for f in latex_files]:
        print(f"\n正在转换 {target_file} ...")
        result = convert_latex_to_docx(target_file)
        if result:
            print(f"转换成功: {result}")
        else:
            print("转换失败，可能需要手动安装pandoc")
    else:
        print(f"未找到 {target_file}")

if __name__ == "__main__":
    main()