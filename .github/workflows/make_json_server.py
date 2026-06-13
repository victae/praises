import os
import json
import re

lyrics_dir = "lyrics"
output_json_path = "ccm_data.json"
html_path = "index.html"

print("서버 로봇: 초경량 ccm_data.json 생성 및 캐시 버전 갱신을 시작합니다...")

if os.path.exists(lyrics_dir):
    ccm_list = []
    generated_id = 1
    for filename in os.listdir(lyrics_dir):
        if filename.endswith(".txt"):
            name_without_ext = os.path.splitext(filename)[0]
            ccm_list.append({"id": generated_id, "title": name_without_ext})
            generated_id += 1

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(ccm_list, f, ensure_ascii=False, indent=4)
    print(f" -> {len(ccm_list)}곡 색인 완료!")

if os.path.exists(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()
    match = re.search(r'ccm_data\.json\?v=(\d+)', content)
    if match:
        current_version = int(match.group(1))
        next_version = current_version + 1
        content = content.replace(f'ccm_data.json?v={current_version}', f'ccm_data.json?v={next_version}')
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f" -> 캐시 버전 자동 업그레이드 완료 (v={next_version})")