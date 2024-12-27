# Kestrel-Trading

This is Kestrel Trading Project.

## Installation

### TA-Lib Dependencies 설치

See the TA-Lib ([https://github.com/TA-Lib/ta-lib-python](https://github.com/TA-Lib/ta-lib-python))


Dependencies ta-lib 설치

```
brew install ta-lib
```

.bash_profile 파일 수정

```
export TA_INCLUDE_PATH="$(brew --prefix ta-lib)/include"
export TA_LIBRARY_PATH="$(brew --prefix ta-lib)/lib"
```

### pyenv 설치

See the pyenv ([https://github.com/pyenv/pyenv](https://github.com/pyenv/pyenv))

```
brew install pyenv
```

.bash_profile 파일 수정
```
export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
```

### pyenv 환경 python 설치

```
pyenv install 3.11
pyenv global 3.11
```

python 버전 체크
```
python --version
```

### poetry 설치 및 셋팅

See the poetry ([https://python-poetry.org/docs](https://python-poetry.org/docs))

poetry 설치

```
pip3 install poetry
```

poetry update 실행

```
poetry update
```

poetry shell 실행

```
poetry shell
```

## Tool Tasks

See the poethepoet ([https://github.com/nat-n/poethepoet](https://github.com/nat-n/poethepoet))

### FastAPI Sevice Start

Service 시작

```
poe start
```

poe start 설정 관련 pyproject.toml 파일 참고

```
...

[tool.poe.tasks]
start = "uvicorn main:app --reload --port 8010"

...
```