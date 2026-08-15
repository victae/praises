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
    """확장자, 출처(-물소리, -찬미예수, -하나복 등), 번호(_0123)를 모두 걷어낸 순수 곡 제목"""
    name_no_ext = os.path.splitext(filename)[0]
    name_norm = norm(name_no_ext)
    # 하이픈(-) 또는 언더바(_) 앞의 알맹이 곡 제목만 추출
    pure = re.split(r'[-_]', name_norm)[0].strip()
    return pure

def simplify_key(title):
    """띄어쓰기, 특수문자, 대소문자를 무시하는 정규화 키"""
    t = norm(title).lower()
    return re.sub(r'[\s\(\)\!\?\,\.\'\"\_]', '', t)

def build_data():
    lyrics_files = [f for f in os.listdir(LYRICS_DIR) if f.lower().endswith('.txt')] if os.path.exists(LYRICS_DIR) else []
    image_files = [f for f in os.listdir(IMAGES_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))] if os.path.exists(IMAGES_DIR) else []

    # 1. 모든 악보 이미지 파일을 '순수 제목' 기준으로 분류
    image_db = {} # key: simplify_key(pure_title) -> list of filenames
    for img in image_files:
        pure_t = get_pure_title(img)
        k = simplify_key(pure_t)
        if k not in image_db:
            image_db[k] = []
        if img not in image_db[k]:
            image_db[k].append(img)

    # 2. 곡 데이터 생성 (가사 파일 기반)
    songs_map = {} # key: simplify_key(pure_title) -> song_dict

    for txt in lyrics_files:
        pure_t = get_pure_title(txt)
        k = simplify_key(pure_t)

        # 가사 파일 읽기
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

        if k not in songs_map:
            songs_map[k] = {
                "title": pure_t,
                "lyrics": lyrics_text,
                "images": []
            }
        else:
            # 더 긴 가사가 있으면 업데이트
            if len(lyrics_text) > len(songs_map[k]["lyrics"]):
                songs_map[k]["lyrics"] = lyrics_text

    # 3. 악보 이미지 연결 (양방향 탐색)
    for k, song in songs_map.items():
        if k in image_db:
            song["images"] = image_db[k]
        else:
            # 부분 일치 보조 탐색 (혹시 모를 미세한 차이 커버)
            for img_k, img_list in image_db.items():
                if k in img_k or img_k in k:
                    song["images"].extend(img_list)
            song["images"] = list(set(song["images"]))

    # 4. 가사는 없고 악보만 있는 곡들도 빠짐없이 추가
    for img_k, img_list in image_db.items():
        if img_k not in songs_map:
            pure_t = get_pure_title(img_list[0])
            songs_map[img_k] = {
                "title": pure_t,
                "lyrics": "",
                "images": img_list
            }

    # 5. 가나다 순 정렬 및 ccm_data.json 저장
    final_list = list(songs_map.values())
    final_list.sort(key=lambda x: x["title"])

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_list, f, ensure_ascii=False, indent=2)

    # 매칭 결과 통계 출력
    with_images = sum(1 for s in final_list if len(s["images"]) > 0)
    print(f"🎉 정리 완료!")
    print(f"- 총 찬양 곡 수: {len(final_list)}곡")
    print(f"- 악보가 정상 연결된 곡: {with_images}곡 (전체 대비 {round(with_images/len(final_list)*100, 1)}%)")

if __name__ == '__main__':
    build_data()