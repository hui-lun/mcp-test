FROM python:3.12-slim

# 安裝 Node.js 與相關工具（包含 npx）
RUN apt-get update && apt-get install -y curl gnupg ca-certificates && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 設定工作目錄
WORKDIR /app

# 複製 requirements.txt 並安裝 Python 依賴
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 預設執行 bash，讓你手動進入 container 開發
CMD ["/bin/bash"]

