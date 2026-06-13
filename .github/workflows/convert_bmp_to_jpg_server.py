import os
from PIL import Image

images_dir = "images" # 서버 환경 맞춤 상대경로
print("서버 로봇: 모든 bmp 파일을 jpg로 일괄 변환합니다...")

if os.path.exists(images_dir):
    for filename in os.listdir(images_dir):
        if filename.lower().endswith('.bmp'):
            bmp_path = os.path.join(images_dir, filename)
            name_without_ext = os.path.splitext(filename)[0]
            jpg_path = os.path.join(images_dir, f"{name_without_ext}.jpg")
            try:
                with Image.open(bmp_path) as img:
                    img.convert('RGB').save(jpg_path, 'JPEG', quality=90)
                os.remove(bmp_path)
                print(f"[성공] 변환: {filename} -> {name_without_ext}.jpg")
            except Exception as e:
                print(f"[에러] {filename}: {e}")