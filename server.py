from flask import Flask, request, render_template_string
from flask_cors import CORS
import os
import requests
import re
import urllib.parse
import html as html_parser
import json

app = Flask(__name__)
CORS(app)

KAKAO_APP_KEY = os.environ.get("KAKAO_APP_KEY", "")

def get_daum_images_brute_force(keyword):
    results = []
    try:
        encoded_keyword = urllib.parse.quote(keyword)
        url = f"https://search.daum.net/search?w=tot&q={encoded_keyword}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            html_content = response.text
            raw_matches = re.findall(r'<img[^>]+src="([^"]+)"[^>]+alt="([^"]+)"', html_content)
            raw_matches_reverse = re.findall(r'<img[^>]+alt="([^"]+)"[^>]+src="([^"]+)"', html_content)
            
            combined_raw = [{"src": src, "alt": alt} for src, alt in raw_matches] + \
                           [{"src": src, "alt": alt} for alt, src in raw_matches_reverse]
                
            for item in combined_raw:
                src = item["src"]
                alt = item["alt"].strip()
                if "argon" not in src and "dn/bt" not in src: continue
                if "ico_" in src or "icon" in src or alt == "이미지" or not alt: continue
                if any(r['imageUrl'] == src for r in results): continue
                
                alt = html_parser.unescape(alt)
                if len(alt) > 22: alt = alt[:20] + "..."
                    
                results.append({"title": alt, "imageUrl": src})
                if len(results) >= 3: break
    except Exception as e:
        print(f"Error: {e}")
        
    generic_fallback = "https://k.kakaocdn.net/14/dn/btqCn7WOmw5/l97ZWSXdaC9sz9gJMf1K01/o.jpg"
    while len(results) < 2:
        results.append({"title": f"'{keyword}' 관련 정보 {len(results)+1}", "imageUrl": generic_fallback})
        
    return results[:3]

@app.route('/')
def sharp_search():
    keyword = request.args.get('q', '').strip()
    if not keyword:
        return "<h3>공유할 단어를 선택하고 단축키를 눌러주세요.</h3>"
        
    search_results = get_daum_images_brute_force(keyword)
    target_url = f"https://m.search.daum.net/search?w=tot&q={urllib.parse.quote(keyword)}"
    
    contents_data = []
    preview_items_html = ""
    
    for item in search_results:
        content_item = {
            "title": item["title"],
            "description": "클릭 시 Daum 검색으로 이동",
            "link": {"mobileWebUrl": target_url, "webUrl": target_url}
        }
        if "kakaolink" not in item["imageUrl"]:
            content_item["imageUrl"] = item["imageUrl"]
            img_tag_html = f'<img class="preview-img" src="{item["imageUrl"]}" alt="미리보기">'
        else:
            img_tag_html = '<div style="font-size: 11px; color: #ccc; border: 1px dashed #ddd; padding: 4px; border-radius: 4px;">이미지 없음</div>'

        contents_data.append(content_item)
        preview_items_html += f"""
        <div class="preview-item">
            <div class="preview-text">
                <div class="preview-title">{item['title']}</div>
                <div class="preview-desc">클릭 시 Daum 검색으로 이동</div>
            </div>
            {img_tag_html}
        </div>"""

    return render_template_string(f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>카카오톡 샵검색</title>
    <script src="https://t1.kakaocdn.net/kakao_js_sdk/2.7.2/kakao.min.js"></script>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; text-align: center; padding: 40px 10px; background-color: #f5f6fa; color: #333; }}
        .container {{ background: white; padding: 30px 20px; display: inline-block; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.08); max-width: 400px; width: 100%; box-sizing: border-box; }}
        .keyword-badge {{ background-color: #e1f5fe; color: #0288d1; padding: 6px 14px; border-radius: 20px; font-weight: bold; display: inline-block; margin-bottom: 20px; }}
        .preview-box {{ border: 1px solid #e1e3e8; border-radius: 8px; text-align: left; margin-bottom: 25px; background: #fff; overflow: hidden; }}
        .preview-header {{ background: #fafafa; padding: 12px 16px; font-weight: bold; border-bottom: 1px solid #f0f0f0; color: #191919; font-size: 14px; }}
        .preview-item {{ display: flex; justify-content: space-between; align-items: center; padding: 14px 16px; border-bottom: 1px solid #f6f6f6; }}
        .preview-item:last-child {{ border-bottom: none; }}
        .preview-text {{ flex: 1; padding-right: 12px; }}
        .preview-title {{ font-size: 14px; font-weight: 500; color: #222; line-height: 1.4; word-break: break-all; }}
        .preview-desc {{ font-size: 11px; color: #999; margin-top: 3px; }}
        .preview-img {{ width: 55px; height: 55px; object-fit: cover; border-radius: 4px; border: 1px solid #f0f0f0; }}
        .btn {{ background-color: #fee500; color: #191919; border: none; padding: 15px 28px; font-weight: bold; border-radius: 8px; cursor: pointer; font-size: 16px; width: 100%; box-sizing: border-box; transition: background 0.2s; }}
        .btn:hover {{ background-color: #fada0a; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="keyword-badge"># {keyword}</div>
        <div class="preview-box">
            <div class="preview-header">전송할 데이터 미리보기</div>
            {preview_items_html}
        </div>
        <button id="shareBtn" class="btn">카카오톡 공유하기</button>
    </div>
    <script>
        if (!Kakao.isInitialized()) {{ Kakao.init('{KAKAO_APP_KEY}'); }}
        document.getElementById('shareBtn').addEventListener('click', function() {{
            Kakao.Share.sendDefault({{
                objectType: 'list',
                headerTitle: '# 샵검색: {keyword}',
                headerLink: {{ mobileWebUrl: '{target_url}', webUrl: '{target_url}' }},
                contents: {json.dumps(contents_data)},
                buttons: [{{ title: '검색 결과 전체보기', link: {{ mobileWebUrl: '{target_url}', webUrl: '{target_url}' }} }}]
            }});
        }});
    </script>
</body>
</html>
""")
