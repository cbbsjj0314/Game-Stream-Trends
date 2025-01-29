![Python](https://img.shields.io/badge/Python-3.11.8-blue?logo=python&logoColor=white)

# Game-Stream-Trends 프로젝트 설정 가이드

이 문서는 프로젝트를 설정하는 방법을 안내합니다.

---

## 1️⃣ 프로젝트 클론 및 이동
GitHub에서 프로젝트를 클론하고 디렉터리로 이동
```sh
git clone https://github.com/cbbsjj0314/Game-Stream-Trends.git
cd Game-Stream-Trends
```

## 2️⃣ Poetry 설치 (한 번만 실행)
Poetry가 설치되지 않았다면 아래 명령어로 설치
#### ▶ Mac
```sh
# 1. Poetry 설치
curl -sSL https://install.python-poetry.org | python3 -

# 2. 환경 변수 추가 (영구 적용)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc && source ~/.zshrc

# 3. 프로젝트 폴더로 가서 Poetry에 python3.11 적용
cd /path/to/your/project
poetry env use python3.11
```

#### ▶ Window
```powershell
# 1. Poetry 설치
curl.exe -sSL https://install.python-poetry.org | python -

# 2. 환경 변수 추가 (영구 적용)
[Environment]::SetEnvironmentVariable("Path", [Environment]::GetEnvironmentVariable("Path", "User") + ";$env:USERPROFILE\AppData\Roaming\Python\Scripts", "User")

# 3. 환경 변수 새로고침 (현재 세션에서 즉시 적용)
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "User") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "Machine")

# 4. 프로젝트 폴더로 가서 Poetry에 python3.11 적용
cd "C:\path\to\your\project"
poetry env use python3.11
```

## 3️⃣ 가상 환경 생성 및 의존성 설치
다음 명령어를 실행하여 프로젝트의 가상 환경을 만들고 필요한 패키지를 설치
```sh
poetry install --with dev
```

## 4️⃣ Airflow 및 MinIO 실행
#### ▶ Airflow 실행
```sh
cd dev/airflow
docker compose up --build -d
```

#### ▶ MinIO 실행
```sh
cd dev/minio
docker compose up --bulid -d
```
