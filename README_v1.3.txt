ScoreClean v1.3 統合版

1. Python 3.10+ をインストール。
2. pip install -r requirements.txt
3. OPENAI_API_KEY を環境変数に設定（APIキーをブラウザーに入れない）。
4. python ai_server.py
5. http://localhost:8765 を開く。
6. AI読取欄で画像を選択、解析URLに http://localhost:8765/api/recognize を指定。
7. 「写真から一括解析」を押す。補正・罫線候補の可視化とAI読取を順番に実行。
8. JSON結果を必ず確認・修正し「確認した内容を反映」を押す。
9. 「清書用スコア表を印刷」で印刷/PDF保存。

注意：線検出は画像処理による候補推定であり、原本と完全一致する座標認識ではありません。AIは打席・走塁の誤読があり得ます。元の写真を確認してください。
補正は紙の外形を検出できた場合のみ実施。マス内の複数打席、交代選手、複雑な進塁経路は完全自動再現できません。
既存LocalStorage scoreclean.v1 / scoreclean.diagrams.v1 を維持します。元データを置換せず、空欄のみ補完します。事前にJSONバックアップを推奨します。
手入力とSVG清書はオフライン可。OpenCV画像補正はローカルサーバーが必要。AI読取はインターネット接続が必要。
