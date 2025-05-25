import os

# Use the current working directory as the root
root_dir = os.getcwd()

# Substrings in folder names to exclude (case-insensitive)
exclude_dir_keywords = [
    '.venv', 'venv', 'node_modules', '__pycache__', '.git',
    'vendor', 'profile', 'cache', 'gpu', 'chrome', 'storage',
    'extension', 'service worker', 'local storage', 'session',
    'network', 'indexed rules', 'web applications', 'blob_storage',
    'webstorage', 'segmentation', 'shadercache', 'appdata',
    'db', 'log', 'metrics', 'mediafoundation', 'ondevice',
    'component_crx_cache', 'extensions_crx_cache',
    'nmmhkkeg', 'ihcjicgdan', 'default', 'temp'
]

# Show only these file types (source code & config files)
include_file_exts = {
    '.ts', '.js', '.jsx', '.json', '.html', '.css',
    '.svelte', '.py', '.md', '.txt', '.yml', '.yaml'
}

def should_exclude_dir(dirname):
    name = dirname.lower()
    return any(keyword in name for keyword in exclude_dir_keywords)

def should_include_file(filename):
    return os.path.splitext(filename)[1] in include_file_exts

def print_tree(start_path, prefix=''):
    try:
        for item in sorted(os.listdir(start_path)):
            path = os.path.join(start_path, item)

            if os.path.isdir(path):
                if should_exclude_dir(item):
                    continue
                print(f"{prefix}📁 {item}")
                print_tree(path, prefix + '    ')
            elif should_include_file(item):
                print(f"{prefix}📄 {item}")
    except Exception as e:
        print(f"{prefix}[Error accessing] {start_path}: {e}")

print(f"🗂️  Project structure (filtered) in: {root_dir}")
print_tree(root_dir)
