# type: ignore
import os
import argparse

EXTENSION_TO_LANG = {
    '.py': 'python', '.js': 'javascript', '.jsx': 'javascript',
    '.ts': 'typescript', '.tsx': 'typescript', '.java': 'java',
    '.c': 'c', '.cpp': 'cpp', '.h': 'c', '.hpp': 'cpp',
    '.cs': 'csharp', '.go': 'go', '.rb': 'ruby', '.rs': 'rust',
    '.swift': 'swift', '.kt': 'kotlin', '.php': 'php', '.html': 'html',
    '.css': 'css', '.scss': 'scss', '.sass': 'sass', '.less': 'less',
    '.json': 'json', '.xml': 'xml', '.yaml': 'yaml', '.yml': 'yaml',
    '.md': 'markdown', '.sh': 'bash', '.bash': 'bash', '.zsh': 'bash',
    '.ps1': 'powershell', '.sql': 'sql', '.lua': 'lua', '.pl': 'perl', '.r': 'r'
}

EXCLUDED_EXTENSIONS = {
    '.exe', '.dll', '.bin', '.pyd',  # Binary
    '.tmp', '.log', '.cache', '.swp',  # Temporary
    '.class', '.o', '.pyc', '.pyo', '.so'  # Compiled
}

def build_tree(included_files, target_dir):
    root = {'name': '.', 'is_dir': True, 'children': []}
    for file_path in included_files:
        rel_path = os.path.relpath(file_path, target_dir)
        components = rel_path.split(os.sep)
        dir_components = components[:-1]
        file_name = components[-1]

        current_node = root
        for dir_name in dir_components:
            found = False
            for child in current_node['children']:
                if child['name'] == dir_name and child['is_dir']:
                    current_node = child
                    found = True
                    break
            if not found:
                new_node = {'name': dir_name, 'is_dir': True, 'children': []}
                current_node['children'].append(new_node)
                current_node = new_node
        file_node = {'name': file_name, 'is_dir': False, 'children': []}
        current_node['children'].append(file_node)
    return root

def generate_tree_lines(node, indent='', is_last=False):
    lines = []
    if node['name'] != '.':
        connector = '└── ' if is_last else '├── '
        lines.append(f"{indent}{connector}{node['name']}")
        indent += '    ' if is_last else '│   '
    else:
        lines.append('.')
    
    if node['is_dir']:
        children = node['children']
        for i, child in enumerate(children):
            child_is_last = i == len(children) - 1
            lines += generate_tree_lines(child, indent, child_is_last)
    return lines

def main():
    parser = argparse.ArgumentParser(
        description='📌 Generate a Markdown file containing a structured directory tree and code content.',
        epilog='''
        Example Usage:
        --------------
        1️⃣ Collect all code files and save to output.md:
           python collect_code_md.py /path/to/project

        2️⃣ Specify output filename:
           python collect_code_md.py /path/to/project --output my_code.md

        3️⃣ Filter by keywords (e.g., files containing "actor" or "category" in their names):
           python collect_code_md.py /path/to/project --keywords actor category
        '''
    )
    parser.add_argument('directory', help='📁 The target directory to scan')
    parser.add_argument('--output', default='output.md', help='📄 Output Markdown file (default: output.md)')
    parser.add_argument('--keywords', nargs='*', default=[], help='🔍 Filter filenames by keywords (optional)')

    args = parser.parse_args()

    target_dir = args.directory
    keywords = args.keywords
    output_file = args.output

    print(f"🔍 Scanning directory: {target_dir}")

    included_files = []
    for root_dir, _, files in os.walk(target_dir):
        for file in files:
            file_path = os.path.join(root_dir, file)
            ext = os.path.splitext(file)[1].lower()

            if ext in EXCLUDED_EXTENSIONS:
                continue  # Skip unwanted files

            if keywords:
                if any(keyword.lower() in file.lower() for keyword in keywords):
                    included_files.append(file_path)
            else:
                included_files.append(file_path)

    if not included_files:
        print("⚠️ No matching code files found.")
        return

    print(f"✅ Found {len(included_files)} matching files. Processing...")

    # Build directory tree structure
    tree_root = build_tree(included_files, target_dir)
    tree_lines = generate_tree_lines(tree_root)
    dir_structure = '\n'.join(tree_lines)

    # Prepare files content
    files_content = []
    for file_path in included_files:
        rel_path = os.path.relpath(file_path, target_dir)
        header_path = './' + rel_path.replace(os.sep, '/')
        ext = os.path.splitext(file_path)[1].lower()
        lang = EXTENSION_TO_LANG.get(ext, '')

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(100000)  # Read up to 100KB
        except UnicodeDecodeError:
            content = "// Binary or non-UTF-8 content not displayed.\n"
        except Exception as e: # pylint: disable=PylintW0718:broad-exception-caught
            content = f"// Error reading file: {str(e)}\n"

        files_content.append(f"## {header_path}\n\n```{lang}\n{content}\n```\n\n")

    # Write to output file
    with open(output_file, 'w', encoding='utf-8') as md_file:
        md_file.write("# 📂 Directory Structure\n\n")
        md_file.write(f"<pre>\n{dir_structure}\n</pre>\n\n")
        md_file.write("# 📄 Files\n\n")
        md_file.write('\n'.join(files_content))

    print("🎉 Processing complete!")
    print(f"✅ Markdown file saved at: {os.path.abspath(output_file)}")

if __name__ == '__main__':
    main()
