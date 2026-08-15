import os
import json
import re
import unicodedata

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LYRICS_DIR = os.path.join(BASE_DIR, 'lyrics')
IMAGES_DIR = os.path.join(BASE_DIR, 'images')
OUTPUT_FILE = os.path.join(BASE_DIR, 'ccm_data.json')

def norm(text):
    if not text: return ""
    return unicodedata.normalize('NFC', text).strip()

def get_pure_title(filename):
    """확장자, 출처(-물소리, -찬2000 등), 번호(_0123) 제거"""
    name_no_ext = os.path.splitext(filename)[0]
    name_norm = norm(name_no_ext)
    pure = re.split(r'[-_]', name_norm)[0].strip()
    return pure

def simplify_key(title):
    """띄어쓰기, 특수문자 무시 정규화 키"""
    t = norm(title).lower()
    return re.sub(r'[\s\(\)\!\?\,\.\'\"\_]', '', t)

def build_data():
    lyrics_files = [f for f in os.listdir(LYRICS_DIR) if f.lower().endswith('.txt')] if os.path.exists(LYRICS_DIR) else []
    image_files = [f for f in os.listdir(IMAGES_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))] if os.path.exists(IMAGES_DIR) else []

    # 1. 모든 악보 이미지 파일 인덱싱
    image_db = {} # key: simplify_key -> list of filenames
    for img in image_files:
        pure_t = get_pure_title(img)
        k = simplify_key(pure_t)
        if k not in image_db:
            image_db[k] = []
        if img not in image_db[k]:
            image_db[k].append(img)

    # 2. 가사 파일 데이터 로드
    lyrics_data_list = []
    for txt in lyrics_files:
        pure_t = get_pure_title(txt)
        txt_path = os.path.join(LYRICS_DIR, txt)
        lyrics_text = ""
        for enc in ['utf-8', 'cp949', 'euc-kr']:
            try:
                with open(txt_path, 'r', encoding=enc) as f:
                    lyrics_text = f.read()
                break
            except:
                continue

        lyrics_text = norm(lyrics_text)
        lyrics_data_list.append({
            "filename": txt,
            "title": pure_t,
            "key": simplify_key(pure_t),
            "lyrics": lyrics_text
        })

    # 3. 지능형 매칭 & 병합
    matched_image_keys = set()
    final_songs = []

    # (A) 가사 파일 기준으로 악보 매칭 탐색
    for item in lyrics_data_list:
        k = item["key"]
        matched_images = []
        matched_key_found = None

        # 1차: 제목 완벽 일치 (예: 가서 제자 삼으라)
        if k in image_db:
            matched_images = image_db[k]
            matched_key_found = k
        else:
            # 2차: 교차 탐색 (가사 파일명이나 가사 본문에 악보 제목이 언급되어 있는지 확인)
            # 예: 가사 파일명 '풍요와 평안의 가면을 쓴' <-> 악보 제목 '삶23'
            for img_k, img_list in image_db.items():
                # 악보 제목 키가 가사 제목에 포함되거나 가사 본문 앞부분에 등장하는 경우
                if (img_k in k) or (k in img_k) or (len(img_k) >= 2 and img_k in simplify_key(item["lyrics"][:100])):
                    matched_images = img_list
                    matched_key_found = img_k
                    break

        title_display = item["title"]

        # 만약 원제목(악보명)과 가사 첫줄 제목이 다르면 "삶 23 (풍요와 평안의 가면을 쓴)" 형태로 통합 표시
        if matched_key_found and matched_key_found != k:
            matched_pure_img_title = get_pure_title(image_db[matched_key_found][0])
            if simplify_key(matched_pure_img_title) != k:
                title_display = f"{matched_pure_img_title} ({item['title']})"

        if matched_key_found:
            matched_image_keys.add(matched_key_found)

        final_songs.append({
            "title": title_display,
            "lyrics": item["lyrics"],
            "images": matched_images
        })

    # (B) 가사 파일에 없었던 악보 단독 곡들 추가
    for img_k, img_list in image_db.items():
        if img_k not in matched_image_keys:
            pure_t = get_pure_title(img_list[0])
            final_songs.append({
                "title": pure_t,
                "lyrics": "",
                "images": img_list
            })

    # 4. 중복 및 빈 악보 정리 (악보가 있는 버전을 우선)
    unique_songs = {}
    for song in final_songs:
        k = simplify_key(song["title"])
        if k not in unique_songs:
            unique_songs[k] = song
        else:
            # 기존 것보다 악보가 더 많거나 가사가 길면 덮어쓰기 병합
            if len(song["images"]) > len(unique_songs[k]["images"]):
                unique_songs[k]["images"] = song["images"]
            if len(song["lyrics"]) > len(unique_songs[k]["lyrics"]):
                unique_songs[k]["lyrics"] = song["lyrics"]

    result_list = list(unique_songs.values())
    result_list.sort(key=lambda x: x["title"])

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(result_list, f, ensure_ascii=False, indent=2)

    with_images = sum(1 for s in result_list if len(s["images"]) > 0)
    print(f"🎉 지능형 매칭 완료!")
    print(f"- 총 찬양 곡 수: {len(result_list)}곡")
    print(f"- 악보가 연결된 곡: {with_images}곡 ({round(with_images/len(result_list)*100, 1)}%)")

if __name__ == '__main__':
    build_data()