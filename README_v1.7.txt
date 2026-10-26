ScoreClean v1.7 / AI不要・GitHub Pages用

GitHub Pagesのリポジトリルートに index.html, app.js, local_scan.js, sw.js, sample_scorebook.jpg 等をアップロード。
「AIなし・端末内自動スキャン」で写真を選択し、解析を実行。罫線の番号と行列数を調整し、マスをタップして文字を確認・入力。

自動処理：画像の小角度回転補正、二値化、縦横罫線候補、マス切出し、記入画素候補。
非対応：手書き漢字のOCR、複雑な進塁線・野球記号の意味解釈、遠近歪みの完全補正。手書き文字の完全自動転記は保証できません。
画像は端末内処理。既存LocalStorage scoreclean.v1 を保持。
