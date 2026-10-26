ScoreClean v1.5 AI読取接続修正版

【Windows】
1. Python 3.10以上をインストール
2. ZIPを展開し、scorebook-app フォルダでターミナルを開く
3. py -m pip install -r requirements.txt
4. PowerShell: $env:OPENAI_API_KEY="あなたのAPIキー"
   コマンドプロンプト: set OPENAI_API_KEY=あなたのAPIキー
5. py ai_server.py
6. ブラウザで http://localhost:8765 を開く（index.htmlをダブルクリックしない）
7. http://localhost:8765/api/health で aiConfigured が true か確認
8. 画像を選択して「AI読取開始」または「写真から一括解析」

【注意】
・APIキーはアプリ画面に入力せず、サーバー側の環境変数に設定してください。
・GitHub PagesのみではPython解析サーバーは動作しません。スマホから localhost はPCを指しません。スマホ利用にはHTTPSで公開したAPIサーバーが必要です。
・OpenAI APIは別途課金が必要です。写真はAPIへ送信されます。
・既存LocalStorageデータはそのままです。更新前にJSON保存を推奨します。
・AIの読取精度は保証されません。必ず確認してから反映してください。
・画像補正・罫線解析にはOpenCVが必要です。
