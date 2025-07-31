import sys
import subprocess
import os
import socket
import pygame
import psutil

pygame.init()
pygame.mixer.init()

# Ekran bilgisi
info = pygame.display.Info()
screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
pygame.display.set_caption("MiniPyEngine Ana Menüsü")

font = pygame.font.SysFont("Arial", 48)
small_font = pygame.font.SysFont("Arial", 30)
clock = pygame.time.Clock()

# Renkler
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
BLUE = (70, 130, 180)
BLACK = (0, 0, 0)

# Menü butonları
button_width = 200
button_height = 50
button_x = 100
buttons = {
    "Sunucuyu Başlat": pygame.Rect(button_x, 180, button_width, button_height),
    "Oyunu Başlat": pygame.Rect(button_x, 250, button_width, button_height),
    "Ayarlar": pygame.Rect(button_x, 320, button_width, button_height),
    "Hakkında": pygame.Rect(button_x, 390, button_width, button_height),
    "Çıkış": pygame.Rect(button_x, 460, button_width, button_height)
}

# Varsayılan ayarlar
screen_width = 1920
screen_height = 1080
sensitivity = 20
settings_active = False

# Ayarları yükle
try:
    with open("config", "r") as f:
        for line in f:
            key, value = line.strip().split(":")
            if key == "screen-width":
                screen_width = int(value)
            elif key == "screen-height":
                screen_height = int(value)
            elif key == "sensitivity":
                sensitivity = int(value)
except:
    print("⚠️  Ayar dosyası yüklenemedi, varsayılan değerler kullanılacak.")

# Arkaplan resmi
try:
    bg_image = pygame.image.load("textures/main.png")
except:
    bg_image = pygame.image.load("textures/missing.png")

# Ayarları kaydet
def save_config():
    with open("config", "w") as f:
        f.write(f"server-ip:127.0.0.1\n")
        f.write(f"server-port:7532\n")
        f.write(f"screen-width:{screen_width}\n")
        f.write(f"screen-height:{screen_height}\n")
        f.write(f"sensitivity:{sensitivity}\n")

def draw_background():
    scaled_bg = pygame.transform.scale(bg_image, (info.current_w, info.current_h))
    screen.blit(scaled_bg, (0, 0))

def draw_menu():
    draw_background()
    mouse_pos = pygame.mouse.get_pos()

    for text, rect in buttons.items():
        is_hovered = rect.collidepoint(mouse_pos)
        button_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        if is_hovered:
            button_surface.fill((255, 255, 0, 160))
            if not hasattr(draw_menu, "hovered") or draw_menu.hovered != text:
                draw_menu.hovered = text
                try:
                    pygame.mixer.Sound("sounds/buttonmenu.mp3").play()
                except:
                    pass
        else:
            button_surface.fill((0, 0, 0, 0))

        screen.blit(button_surface, rect.topleft)
        label = font.render(text, True, WHITE)
        label = pygame.transform.smoothscale(label, label.get_size())
        label_rect = label.get_rect(center=rect.center)
        screen.blit(label, label_rect)

    pygame.display.flip()

# Ayar menüsü
resolution_options = [
    ("640x480", (640, 480), pygame.Rect(100, 200, 200, 40)),
    ("800x600", (800, 600), pygame.Rect(100, 250, 200, 40)),
    ("1280x720", (1280, 720), pygame.Rect(100, 300, 200, 40)),
    ("1920x1080", (1920, 1080), pygame.Rect(100, 350, 200, 40)),
    ("2560x1440 (2K)", (2560, 1440), pygame.Rect(100, 400, 200, 40)),
    ("3840x2160 (4K)", (3840, 2160), pygame.Rect(100, 450, 200, 40))
]
sens_rect = pygame.Rect(100, 510, 300, 40)
back_rect = pygame.Rect(100, 570, 200, 50)

def draw_settings():
    draw_background()
    mouse_pos = pygame.mouse.get_pos()

    for label_text, res, rect in resolution_options:
        is_selected = (screen_width, screen_height) == res
        is_hovered = rect.collidepoint(mouse_pos)

        surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        if is_selected:
            surface.fill((255, 255, 0, 160))
        elif is_hovered:
            surface.fill((255, 255, 255, 40))
        else:
            surface.fill((0, 0, 0, 0))

        screen.blit(surface, rect.topleft)
        label = small_font.render(label_text, True, WHITE)
        label_rect = label.get_rect(center=rect.center)
        screen.blit(label, label_rect)

    pygame.draw.rect(screen, BLUE, sens_rect, border_radius=12)
    sens_label = small_font.render(f"Hassasiyet: {sensitivity} (tıklayın +/-)", True, WHITE)
    screen.blit(sens_label, sens_rect.move(10, 8))

    pygame.draw.rect(screen, GRAY, back_rect, border_radius=12)
    back_label = small_font.render("Geri", True, WHITE)
    screen.blit(back_label, back_rect.move(10, 10))

    pygame.display.flip()

def run_game():
    for p in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = p.info.get('cmdline')
            if cmdline and any("StartGame.py" in part for part in cmdline):
                print("⚠️  StartGame zaten çalışıyor, tekrar başlatılmadı.")
                return
        except:
            pass
    try:
        subprocess.Popen([sys.executable, "StartGame.py", "--launched-from-menu"])
        print("✅ StartGame başlatıldı.")
    except Exception as e:
        print("🚫 StartGame başlatılamadı:", e)

running = True

while running:
    if settings_active:
        draw_settings()
    else:
        draw_menu()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if settings_active:
                save_config()
                settings_active = False
            else:
                running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if settings_active:
                for label, res, rect in resolution_options:
                    if rect.collidepoint(pos):
                        screen_width, screen_height = res
                        try:
                            pygame.mixer.Sound("sounds/buttonmenu.mp3").play()
                        except:
                            pass
                if sens_rect.collidepoint(pos):
                    sensitivity = 0 if sensitivity >= 100 else sensitivity + 5
                if back_rect.collidepoint(pos):
                    save_config()
                    settings_active = False
                    try:
                        pygame.mixer.Sound("sounds/buttonmenu.mp3").play()
                    except:
                        pass
            else:
                if buttons["Sunucuyu Başlat"].collidepoint(pos):
                    try:
                        pygame.mixer.Sound("sounds/buttonmenu.mp3").play()
                    except:
                        pass
                    parent_dir = os.path.abspath(os.path.join(os.getcwd(), ".."))
                    server_path = os.path.join(parent_dir, "game-server", "Server.py")
                    subprocess.Popen([sys.executable, server_path])
                    print("✅ Sunucu başlatıldı.")

                elif buttons["Oyunu Başlat"].collidepoint(pos):
                    run_game()
                    try:
                        pygame.mixer.Sound("sounds/buttonmenu.mp3").play()
                    except:
                        pass

                elif buttons["Ayarlar"].collidepoint(pos):
                    settings_active = True
                    try:
                        pygame.mixer.Sound("sounds/buttonmenu.mp3").play()
                    except:
                        pass

                elif buttons["Hakkında"].collidepoint(pos):
                    try:
                        pygame.mixer.Sound("sounds/buttonmenu.mp3").play()
                    except:
                        pass
                    try:
                        import tkinter as tk
                        from tkinter import scrolledtext
                        with open("about.txt", "r", encoding="utf-8") as af:
                            content = af.read()
                        def show_hakkinda():
                            root = tk.Tk()
                            root.title("Hakkında MiniPyEngine")
                            root.geometry("700x900")
                            text_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Arial", 12))
                            text_box.insert(tk.END, content)
                            text_box.config(state=tk.DISABLED)
                            text_box.pack(expand=True, fill='both')
                            root.mainloop()
                        show_hakkinda()
                    except Exception as e:
                        print("🚫 Hakkında metni yüklenemedi:", e)

                elif buttons["Çıkış"].collidepoint(pos):
                    try:
                        for p in psutil.process_iter(['pid', 'name', 'cmdline']):
                            cmdline = p.info.get('cmdline')
                            if cmdline and any("main.py" in part or "StartGame.py" in part for part in cmdline):
                                p.terminate()
                        print("✅ Uygulama kapatılıyor.")
                    except:
                        print("⚠️  Uygulama kapatılırken hata oluştu.")
                    running = False

pygame.quit()
