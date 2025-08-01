import json

# Load configuration
def load_config():
    with open(CONFIG_FILE, 'r') as file:
        return json.load(file)

CACHE_DIRECTORY = '.cache'
OUTPUT_DIRECTORY = 'output'

CONFIG_FILE = 'gpt.knowledge.compiler.json'
CONFIG = load_config()

# Files to ignore
IGNORE_NAMES = [

    # Default Output Filename for merged data
    'merged_data.json',

    # Common system and hidden files
    '.DS_Store', 'Thumbs.db', '.git', '.svn', '.hg',

    # Dependency directories
    'node_modules', 'venv', 'env', '.env', 'bower_components',

    # Package manager files
    'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml', 'pnpm-lock.json', 'composer.json', 'composer.lock', 'composer.lock',
    # 'package.json',
    # 'composer.json',

    # Configuration and build files
    # '.babelrc', '.eslintrc', '.prettierrc', 'webpack.config.js', 'tsconfig.json',

    # Log files
    '*.log',

    # Compiled files
    '*.pyc', '*.class', '*.o', '*.so',

    # Backup files
    '*~', '*.bak', '*.tmp', '*.temp',

    # Editor and IDE directories
     '.husky','.idea', '.vscode', '.eclipse',
    '.github', '.gitignore', '.gitlab-ci.yml', '.dockerignore',
    # '.eslint.json'

    # Binary and executable files
    '*.exe', '*.dll', '*.bin', '*.out', '*.apk', '*.ipa',

    # Image files
    # '*.png', '*.jpg', '*.jpeg', '*.gif', '*.bmp', '*.tiff',
    '.ico',

    # Audio and video files
    '*.mp3', '*.wav', '*.mp4', '*.avi', '*.mkv', '*.flv',

    # Archive and compressed files
    # '*.zip', '*.tar', '*.gz', '*.bz2', '*.7z', '*.rar', '*.tgz',

    # Document files
    # '*.pdf', '*.doc', '*.docx', '*.xls', '*.xlsx', '*.ppt', '*.pptx', '*.txt', '*.csv',

    # Other files
    '.travis.yml',

    # 'Dockerfile', 'Makefile', 'LICENSE', 'README.md', 'CHANGELOG.md'
    '.skp', '.afdesign', '.webm',

]
