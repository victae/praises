import os
import json
import unicodedata

# 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LYRICS_DIR = os.path.join(BASE_DIR, 'lyrics')
IMAGES_DIR = os.path.join(BASE_DIR, 'images')
OUTPUT_FILE = os.path.join(BASE_DIR, 'ccm_data.json')

def clean_text(text):
    return unicodedata.normalize('NFC', text).strip()

def build_ccm_json():
    # 1. 악보 이미지 파일 목록 스캔 & 분류
    image_files = os.listdir(IMAGES_DIR) if os.path.exists(IMAGES_DIR) else []
    image_map = {} # Key: 대표제목, Value: [매칭되는 악보 파일명들]

    for img_name in image_files:
        if not img_name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
            continue
        
        name_no_ext = os.path.splitext(img_name)[0]
        norm_name = clean_text(name_no_ext)
        
        # 하이픈(-) 앞의 순수 곡 제목 추출 (예: "호산나-물소리" -> "호산나")
        pure_title = norm_name.split('-')[0].strip()
        
        if pure_title not in image_map:
            image_map[pure_title] = []
        image_map[pure_title].append(img_name)

    # 2. 가사 txt 파일 목록 스캔 & 통합
    lyrics_files = os.listdir(LYRICS_DIR) if os.path.exists(LYRICS_DIR) else []
    result_data = []
    processed_titles = set()

    for txt_name in lyrics_files:
        if not txt_name.lower().endswith('.txt'):
            continue
            
        song_title = clean_text(os.path.splitext(txt_name)[0])
        pure_title = song_title.split('-')[0].strip()
        
        # 가사 파일 읽기 (UTF-8 우선, CP949 보조)
        txt_path = os.path.join(LYRICS_DIR, txt_name)
        lyrics_content = ""
        try:
            with open(txt_path, 'r', encoding='utf-8') as f:
                lyrics_content = f.read()
        except:
            try:
                with open(txt_path, 'r', encoding='cp949') as f:
                    lyrics_content = f.read()
            except:
                lyrics_content = ""

        # 매칭되는 악보들 가져오기
        matched_images = image_map.get(pure_title, image_map.get(song_title, []))

        result_data.append({
            "title": song_title,
            "lyrics": clean_text(lyrics_content),
            "images": matched_images
        })
        processed_titles.add(pure_title)
        processed_titles.add(song_title)

    # 3. 가사는 없는데 악보 이미지만 있는 곡들도 챙겨서 추가
    for pure_title, img_list in image_map.items():
        if pure_title not in processed_titles:
            result_data.append({
                "title": pure_title,
                "lyrics": "",
                "images": img_list
            })

    # 4. 최종 ccm_data.json 저장 (가나다 순 정렬)
    result_data.sort(key=lambda x: x['title'])
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)

    print(f"🎉 변환 완료! 총 {len(result_data)}개의 찬양이 ccm_data.json에 저장되었습니다.")

if __name__ == '__main__':
    build_ccm_json()