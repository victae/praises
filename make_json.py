import os
import json
import re
import unicodedata

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LYRICS_DIR = os.path.join(BASE_DIR, 'lyrics')
IMAGES_DIR = os.path.join(BASE_DIR, 'images')
OUTPUT_FILE = os.path.join(BASE_DIR, 'ccm_data.json')

def norm(text):
    return unicodedata.normalize('NFC', text).strip()

def clean_key(text):
    """띄어쓰기 및 특수문자를 제거하여 유사 제목을 하나로 묶는 비교 키"""
    t = norm(text)
    t = re.sub(r'[-_].*$', '', t) # 출처나 번호 분리
    t = re.sub(r'[\s\(\)\!\?\,\.]', '', t)
    return t.lower()

def extract_source(filename):
    """출처명을 '찬2000', '물소리' 등으로 깔끔하게 정리"""
    name_no_ext = os.path.splitext(filename)[0]
    name_no_ext = norm(name_no_ext)
    
    tag = "일반"
    if '-' in name_no_ext:
        tag = name_no_ext.split('-')[-1].strip()
    elif '_' in name_no_ext:
        tag = '#' + name_no_ext.split('_')[-1].strip()

    # 출처명 통일
    tag = re.sub(r'찬미예수\s*2000|찬미예수', '찬2000', tag)
    tag = re.sub(r'많은\s*물소리', '물소리', tag)
    return tag

def build_data():
    lyrics_files = [f for f in os.listdir(LYRICS_DIR) if f.lower().endswith('.txt')]
    image_files = [f for f in os.listdir(IMAGES_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))]

    # 1. 악보 인덱싱 (클린 키 -> 이미지 목록)
    image_db = {}
    for img in image_files:
        k = clean_key(os.path.splitext(img)[0])
        image_db.setdefault(k, []).append(img)

    # 2. 곡 데이터 조립
    songs_map = {} # 클린 키 -> { title, lyrics, images }

    for txt in lyrics_files:
        raw_name = os.path.splitext(txt)[0]
        k = clean_key(raw_name)
        
        # 순수 제목 추출
        pure_title = norm(raw_name.split('-')[0].split('_')[0].strip())
        
        # 가사 읽기
        txt_path = os.path.join(LYRICS_DIR, txt)
        lyrics_text = ""
        for enc in ['utf-8', 'cp949', 'euc-kr']:
            try:
                with open(txt_path, 'r', encoding=enc) as f:
                    lyrics_text = f.read()
                break
            except:
                continue

        if k not in songs_map:
            songs_map[k] = {
                "title": pure_title,
                "lyrics": norm(lyrics_text),
                "images": []
            }
        else:
            # 가사가 비어있지 않은 것을 우선 채택
            if len(lyrics_text.strip()) > len(songs_map[k]["lyrics"]):
                songs_map[k]["lyrics"] = norm(lyrics_text)

    # 3. 악보 이미지 매칭 연결
    for k, song in songs_map.items():
        if k in image_db:
            song["images"] = image_db[k]

    # 4. 가사는 없고 악보만 있는 곡 추가
    for k, img_list in image_db.items():
        if k not in songs_map:
            raw_name = os.path.splitext(img_list[0])[0]
            pure_title = norm(raw_name.split('-')[0].split('_')[0].strip())
            songs_map[k] = {
                "title": pure_title,
                "lyrics": "",
                "images": img_list
            }

    # 5. 리스트로 변환 및 정렬
    final_list = list(songs_map.values())
    final_list.sort(key=lambda x: x["title"])

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_list, f, ensure_ascii=False, indent=2)

    print(f"🎉 성공! 총 {len(final_list)}곡이 완벽 정리되어 'ccm_data.json'으로 완성되었습니다.")

if __name__ == '__main__':
    build_data()