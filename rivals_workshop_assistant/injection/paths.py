from pathlib import Path

ASSISTANT_FOLDER = Path('assistant')
INJECT_FOLDER = ASSISTANT_FOLDER / Path('.inject')
USER_INJECT_FOLDER = ASSISTANT_FOLDER / Path('user_inject')
DOTFILE_NAME = '.assistant'
DOTFILE_PATH = ASSISTANT_FOLDER / DOTFILE_NAME
INJECT_CONFIG_NAME = 'assistant_config.ini'
INJECT_CONFIG_PATH = ASSISTANT_FOLDER / INJECT_CONFIG_NAME
REPO_OWNER = 'Rivals-Workshop-Community-Projects'
REPO_NAME = 'injector-library'