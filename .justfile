set dotenv-load := true

branch := "dev"

default:
    @just --list --justfile {{ justfile() }}

sync *args:
    rye sync {{args}}

install:
    rye sync --no-lock

pull branch=branch:
    git checkout {{ branch }}
    git pull origin {{ branch }}

update branch=branch: (pull branch)

dev:
    if command -v watchexec >/dev/null 2>&1; then \
        watchexec --watch src --exts py --on-busy-update=restart --stop-signal SIGKILL -- rye run uvicorn src.youtube_search.web:app --host 0.0.0.0 --port 8001 --reload; \
    else \
        rye run uvicorn src.youtube_search.web:app --host 0.0.0.0 --port 8001 --reload; \
    fi

setup:
    # Rye
    curl -sSf https://rye-up.com/get | bash
    echo 'source "$HOME/.rye/env"' >> ~/.bashrc

    # Direnv
    curl -sfL https://direnv.net/install.sh | bash
    echo 'eval "$(direnv hook bash)"' >> ~/.bashrc

    # Install git hooks
    just install-hooks

    @echo "Restart your shell to finish setup!"

format:
    rye run isort --profile=black --skip-gitignore .
    rye run ruff check --fix --exit-zero .
    rye run ruff format .

install-hooks:
    #!/usr/bin/env sh
    # Create pre-commit config file
    rye sync --no-lock
    cat > .pre-commit-config.yaml << 'EOF'
    repos:
    -   repo: https://github.com/pycqa/isort
        rev: 5.13.2
        hooks:
        -   id: isort
            args: ["--profile", "black", "--skip-gitignore"]
            
    -   repo: https://github.com/astral-sh/ruff-pre-commit
        rev: v0.8.4
        hooks:
        -   id: ruff
            args: ["--fix", "--exit-zero"]
        -   id: ruff-format 
    EOF

    # Install pre-commit if not already installed
    if ! command -v pre-commit >/dev/null 2>&1; then
        rye add pre-commit
    fi

    # Install the pre-commit hooks
    pre-commit install

    echo "Pre-commit hooks installed successfully!"