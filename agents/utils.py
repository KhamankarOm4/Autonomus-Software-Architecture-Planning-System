"""
Utility functions for the system.
"""

import os

def read_codebase(path: str) -> str:
    """Reads a file or a whole directory of code files into a single string."""
    if not os.path.exists(path):
        return ""

    if os.path.isfile(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f"--- FILE: {os.path.basename(path)} ---\n" + f.read() + "\n\n"
        except Exception as e:
            return f"Error reading file {path}: {e}"

    # If it's a directory, read all common code files
    allowed_exts = {".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".cpp", ".c", ".h", ".go", ".rs", ".cs", ".rb", ".php"}
    code_content = []
    
    for root, _, files in os.walk(path):
        # skip hidden dirs or common virtual envs/node_modules
        if any(part.startswith('.') for part in root.split(os.sep)) or "node_modules" in root or "venv" in root or "__pycache__" in root:
            continue
            
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in allowed_exts:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        rel_path = os.path.relpath(file_path, path)
                        code_content.append(f"--- FILE: {rel_path} ---\n{f.read()}\n")
                except Exception:
                    pass # ignore unreadable files

    return "\n".join(code_content)

def extract_document_text(file_path: str) -> str:
    """Extracts text from a given PDF, DOCX, or plain text document."""
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == '.pdf':
        try:
            import PyPDF2
            text = []
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text.append(page.extract_text() or "")
            return "\n".join(text)
        except ImportError:
            return "Error: PyPDF2 is not installed. Run `pip install PyPDF2` to read PDFs."
        except Exception as e:
            return f"Error reading PDF: {e}"
            
    elif ext in ['.docx', '.doc']:
        try:
            import docx
            doc = docx.Document(file_path)
            return "\n".join([p.text for p in doc.paragraphs])
        except ImportError:
            return "Error: python-docx is not installed. Run `pip install python-docx` to read DOCX files."
        except Exception as e:
            return f"Error reading DOCX: {e}"
            
    elif ext in ['.txt', '.md']:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        return f"Error: Unsupported document format '{ext}'."

