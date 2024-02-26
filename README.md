## Initial setup

### VSCode Python Development

1. Install the `Python Extension Pack` in VSCode
2. Install `Pylance` extension
3. Install `Mypy Type Checker` extension
4. Open your JSON settings
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

### Initializing the virtual environment

Always, when starting a new terminal, you need to activate the virtual environment:

```bash
source venv/bin/activate
```

or in Windows:

```ps
.\venv\Scripts\Activate.ps1
```

### First time setup

1. Install [Poetry](https://python-poetry.org/docs/), the package manager

2. Install the dependencies:

```bash
poetry install
```

## Running the code

Specify the script number and optionally the nubmer of concurrent workers. The
default is `2` and a maximum of `8`. This maximum is to prevent getting rate
limited by the server.

```bash
python .\lowes\ {script_number} [-c {number_of_workers}]
```
