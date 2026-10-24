"""Reproducible geometry check on the supplied real scorebook image. No OCR accuracy claim."""
from pathlib import Path
from pipeline import process
from cell_mapping import map_cells
import json,base64
p=Path(__file__).parent/'sample_scorebook.jpg'
if not p.exists():raise SystemExit('sample_scorebook.jpg がありません')
r=process(p.read_bytes());r.pop('image',None)
print(json.dumps({'image':p.name,'layout':r,'assessment':'罫線候補のみ。文字・記号の正解データがないため認識精度は未評価。'},ensure_ascii=False,indent=2))
