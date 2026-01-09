import os

video_path = "football_test.mp4"

if os.path.exists(video_path):
    file_size = os.path.getsize(video_path) / (1024 * 1024)
    print(f"✅ Video encontrado: {video_path}")
    print(f"   Tamaño: {file_size:.1f} MB")
else:
    print("❌ Video no encontrado")
    print("   Descarga un video de fútbol y nómbralo 'football_test.mp4'")