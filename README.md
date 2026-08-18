# Local Gemma Assistant

目前版本只實作從終端直接呼叫本機 Ollama。

## 準備模型

安裝並啟動 Ollama，再下載模型：

```powershell
ollama pull gemma3:12b-it-qat
```

## 安裝套件

在虛擬環境內執行：

```powershell
pip install -r requirements.txt
```

## 開始對話

```powershell
python main.py
```

輸入 `q` 或 `quit` 結束對話。

模型名稱、Ollama 網址與生成參數可在 `config.yaml` 調整。
