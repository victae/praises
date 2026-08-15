import os
import unicodedata

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LYRICS_DIR = os.path.join(BASE_DIR, 'lyrics')
IMAGES_DIR = os.path.join(BASE_DIR, 'images')
REPORT_FILE = os.path.join(BASE_DIR, '매칭_진단결과.txt')

def norm(text):
    return unicodedata.normalize('NFC', text).strip()

def analyze():
    lyrics_files = [f for f in os.listdir(LYRICS_DIR) if f.lower().endswith('.txt')]
    image_files = [f for f in os.listdir(IMAGES_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))]

    # 가사 및 악보 제목 파싱
    lyrics_map = {} # 순수제목 -> [파일명목록]
    images_map = {} # 순수제목 -> [파일명목록]

    for f in lyrics_files:
        name_no_ext = norm(os.path.splitext(f)[0])
        pure_title = name_no_ext.split('-')[0].split('_')[0].strip()
        lyrics_map.setdefault(pure_title, []).append(f)

    for f in image_files:
        name_no_ext = norm(os.path.splitext(f)[0])
        pure_title = name_no_ext.split('-')[0].split('_')[0].strip()
        images_map.setdefault(pure_title, []).append(f)

    all_pure_titles = sorted(list(set(list(lyrics_map.keys()) + list(images_map.keys()))), key=lambda x: (x.encode('utf-8')))

    perfect_match = []      # 가사-악보 완벽 매칭
    multi_version = []      # 버전이 여러 개 있는 곡 (찬미예수/물소리 등)
    lyrics_only = []        # 가사만 있고 악보가 없는 곡
    images_only = []        # 악보만 있고 가사가 없는 곡

    for title in all_pure_titles:
        l_list = lyrics_map.get(title, [])
        i_list = images_map.get(title, [])

        if l_list and i_list:
            if len(l_list) > 1 or len(i_list) > 1:
                multi_version.append((title, l_list, i_list))
            else:
                perfect_match.append((title, l_list[0], i_list[0]))
        elif l_list and not i_list:
            lyrics_only.append((title, l_list))
        elif not l_list and i_list:
            images_only.append((title, i_list))

    with open(REPORT_FILE, 'w', encoding='utf-8') as rep:
        rep.write("=" * 60 + "\n")
        rep.write(f"📊 찬양 데이터 매칭 진단 리포트\n")
        rep.write(f"총 고유 찬양 곡 수: {len(all_pure_titles)}곡\n")
        rep.write(f"- 1:1 완벽 매칭: {len(perfect_match)}곡\n")
        rep.write(f"- 다중 버전 매칭(찬미/물소리 등 복수 악보): {len(multi_version)}곡\n")
        rep.write(f"- 가사만 있는 곡 (악보 누락): {len(lyrics_only)}곡\n")
        rep.write(f"- 악보만 있는 곡 (가사 누락): {len(images_only)}곡\n")
        rep.write("=" * 60 + "\n\n")

        rep.write("■ [1] 다중 버전 매칭 곡 (검토 필요 대상)\n")
        for title, l_list, i_list in multi_version:
            rep.write(f"▶ 곡명: [{title}]\n")
            rep.write(f"   - 가사 txt ({len(l_list)}개): {', '.join(l_list)}\n")
            rep.write(f"   - 악보 img ({len(i_list)}개): {', '.join(i_list)}\n")

        rep.write("\n" + "=" * 60 + "\n")
        rep.write("■ [2] 악보만 있고 가사가 없는 곡 목록\n")
        for title, i_list in images_only:
            rep.write(f"   - [{title}]: {', '.join(i_list)}\n")

        rep.write("\n" + "=" * 60 + "\n")
        rep.write("■ [3] 가사만 있고 악보가 없는 곡 목록\n")
        for title, l_list in lyrics_only:
            rep.write(f"   - [{title}]: {', '.join(l_list)}\n")

    print(f"✅ 진단 완료! '{REPORT_FILE}' 파일이 생성되었습니다.")

if __name__ == '__main__':
    analyze()