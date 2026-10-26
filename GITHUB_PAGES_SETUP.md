# ScoreClean v1.6 — GitHub Pages AI設定

1. Cloudflareアカウントで Workers & Pages → Create Worker を作成し、`worker.js` をデプロイします。
2. Worker の Settings → Variables and Secrets に `OPENAI_API_KEY` を **Secret** として登録します。APIキーはGitHubやHTMLに記載しないでください。
3. `ALLOWED_ORIGINS` に `https://ユーザー名.github.io` を設定します（末尾スラッシュなし）。カスタムドメイン利用時はそのOriginを追加。複数はカンマ区切り。
4. GitHub Pagesに `index.html`, `app.js`, `sw.js`, `manifest.webmanifest`, `icon.svg` をアップロードします。GitHub Pagesの公開フォルダのルートに配置してください。
5. ScoreCleanの「解析API URL」に `https://YOUR-WORKER.YOUR-SUBDOMAIN.workers.dev/api/recognize` を入力し「API接続テスト」を押します。成功後、画像を選び「AI読取開始」。
6. 以前の画面が残る場合はページを再読み込みし、PWAを再起動してください。

## 注意
- GitHub Pagesは静的ホスティングです。AI読取には別途Cloudflare WorkerとOpenAI APIの利用設定・料金が必要です。
- クラウド版ではOpenCVによる傾き補正・罫線検出と座標マッピングは未対応。「写真から一括解析」は原画像AI読取へフォールバックします。
- 認識精度は未検証。確認・修正後に反映してください。
- 画像はWorker経由でOpenAIへ送信されます。第三者の個人情報が写る画像は取り扱いに注意してください。
- WorkerのCORS Origin制限はアクセス制御・利用料金保護として十分ではありません。公開サイトでは認証、レート制限、利用上限を追加してください。
- この環境ではCloudflare/OpenAIへの実接続テストは未実施です。
