"""Build a portable review page from campaign copy and actual assets.
Copyright 2026 CaseSprout contributors. Licensed under Apache-2.0.
"""
import html
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
campaign=json.loads((root/'campaign/campaign.json').read_text())
parts=[]
for item in campaign['items']:
    parts.append('<article><h2>'+str(item['beat'])+' · '+html.escape(item['hook'])+'</h2><img src="'+html.escape(item['image'])+'" alt="'+html.escape(item['alt'])+'"><p><b>Audience:</b> '+html.escape(item['audience'])+'</p><p><b>Alt text:</b> '+html.escape(item['alt'])+'</p><h3>LinkedIn</h3><div class="copy">'+html.escape(item['linkedin'])+'</div><h3>X thread</h3>'+''.join('<div class="copy x">'+html.escape(text)+'</div>' for text in item['x'])+'<p><b>Evidence:</b> '+html.escape(', '.join(item['evidence']))+'</p><p><b>Call to action:</b> '+html.escape(item['cta'])+'</p></article>')
(root/'campaign/index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CaseSprout launch campaign review</title><style>body{margin:0;background:#f5f3ed;color:#173d36;font:17px/1.65 system-ui}main{max-width:1000px;margin:auto;padding:48px 24px}h1{font-size:40px;line-height:1.2}h2{line-height:1.3}article{margin:48px 0;padding:30px;background:white;border-radius:14px}img{width:100%;height:auto;border-radius:8px}.copy{white-space:pre-wrap;padding:22px;background:#f4f7f2;border-left:4px solid #235a47}.x{margin:16px 0}a{color:#235a47}</style><main><h1>CaseSprout · English launch kit</h1><p>Five story beats. Prepared copy and inspected assets. Scheduling and publication are recorded separately in scheduling.json; this review page does not claim social publication.</p><p><a href="https://github.com/grishahq/casesprout/releases/tag/v0.1.0a1">Verified public alpha release</a></p>'+''.join(parts)+'</main></html>')
