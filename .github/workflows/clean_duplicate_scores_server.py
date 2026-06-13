import os

images_dir = "images" # 서버 환경 맞춤 상대경로
print("서버 로봇: 중복 악보 파일(JPG/GIF) 청소를 시작합니다...")

if os.path.exists(images_dir):
    all_files = os.listdir(images_dir)
    jpg_names = set()
    gif_files_map = {}

    for filename in all_files:
        name_without_ext, ext = os.path.splitext(filename)
        ext = ext.lower()
        if ext == '.jpg':
            jpg_names.add(name_without_ext)
        elif ext == '.gif':
            gif_files_map[name_without_ext] = filename

    for name in gif_files_map:
        if name in jpg_names:
            gif_to_remove = os.path.join(images_dir, gif_files_map[name])
            try:
                os.remove(gif_to_remove)
                print(f"[성공] 중복 GIF 삭제: {gif_files_map[name]}")
            except Exception as e:
                print(f"[실패] {gif_files_map[name]}: {e}")