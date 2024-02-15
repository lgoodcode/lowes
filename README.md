## VSCode Python Development

1. Install the `Python Extension Pack` in VSCode.
2. Open your JSON settings
    1. Press `F1` and type `Preferences: Open Settings (JSON)`
    2. Add the following settings:
        ```json
          "[python]": {
            "editor.formatOnSave": true,
            "editor.codeActionsOnSave": {
              "source.organizeImports": "explicit"
            },
            "editor.defaultFormatter": "ms-python.black-formatter"
          },
        ```

## Initializing the virtual environment

Always, when starting a new terminal, you need to activate the virtual environment:

```bash
source venv/bin/activate
```

or in Windows:

```ps
.\venv\Scripts\Activate.ps1
```

### First time

1. Install `setuptools`:

```bash
pip install --upgrade setuptools
```

2. Install the modules:

```bash
pip install -r requirements.txt
```
