#!/usr/bin/env python3
import os
import sys
import subprocess
import re
import time
import shutil
import platform
import math
import datetime
from getpass import getpass
from itertools import cycle

# --- КОНФИГУРАЦИЯ ---
LOG_DIR = "/Quasar--installer"
LOG_FILE = f"{LOG_DIR}/install.log"
INSTALLER_DIR = os.path.dirname(os.path.abspath(__file__))

# Создаем директорию для логов
os.makedirs(LOG_DIR, exist_ok=True)

# Псевдографические элементы
H_LINE = '─'
V_LINE = '│'
CORNER_TL = '╭'
CORNER_TR = '╮'
CORNER_BL = '╰'
CORNER_BR = '╯'
T_UP = '╧'
T_DOWN = '╤'
T_LEFT = '╢'
T_RIGHT = '╟'
CROSS = '┼'
ARROW_RIGHT = '▶'
ARROW_LEFT = '◀'

# Анимация спиннера
SPINNER = cycle(['⣷', '⣯', '⣟', '⡿', '⢿', '⣻', '⣽', '⣾'])

# --- ФУНКЦИИ ЛОГИРОВАНИЯ ---
def log_init():
    """Инициализация лог-файла"""
    with open(LOG_FILE, "w") as f:
        f.write(f"Quasar Linux Installer Log\n")
        f.write(f"Started at: {datetime.datetime.now()}\n")
        f.write(f"Python version: {sys.version}\n")
        f.write(f"System: {platform.platform()}\n")
        f.write("-" * 80 + "\n")

def log_message(message):
    """Запись сообщения в лог"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")

def log_command(cmd, output, error=None):
    """Логирование выполнения команды"""
    log_message(f"COMMAND: {cmd}")
    if output:
        log_message(f"OUTPUT: {output[:500]}")  # Логируем первые 500 символов
    if error:
        log_message(f"ERROR: {error}")

# --- ИНТЕРФЕЙСНЫЕ ФУНКЦИИ ---
def clear_screen():
    os.system('clear')

def center_text(text, width=80):
    """Центрирует текст с учётом границ"""
    padding = (width - len(text)) // 2
    return ' ' * max(0, padding) + text

def draw_box(title, width=80, content=None, footer=None):
    """Рисует красивый центрированный блок"""
    # Верхняя граница
    box = CORNER_TL + H_LINE * (width - 2) + CORNER_TR + '\n'
    
    # Заголовок (центрированный)
    title_line = V_LINE + center_text(title, width - 2) + V_LINE + '\n'
    box += title_line
    box += T_RIGHT + H_LINE * (width - 2) + T_LEFT + '\n'
    
    # Контент (центрированный)
    if content:
        for line in content:
            centered = center_text(line, width - 4)
            box += V_LINE + ' ' + centered + ' ' + V_LINE + '\n'
    
    # Нижняя граница
    if footer:
        box += T_RIGHT + H_LINE * (width - 2) + T_LEFT + '\n'
        footer_line = V_LINE + center_text(footer, width - 2) + V_LINE + '\n'
        box += footer_line
    
    box += CORNER_BL + H_LINE * (width - 2) + CORNER_BR
    return box

def print_header():
    clear_screen()
    header = f"""
{CORNER_TL}{H_LINE * 78}{CORNER_TR}
{V_LINE}{' ' * 78}{V_LINE}
{V_LINE}{center_text('██████╗ ██╗   ██╗ █████╗ ███████╗ █████╗ ██████╗', 78)}{V_LINE}
{V_LINE}{center_text('██╔═══██╗██║   ██║██╔══██╗██╔════╝██╔══██╗██╔══██╗', 78)}{V_LINE}
{V_LINE}{center_text('██║   ██║██║   ██║███████║███████╗███████║██████╔╝', 78)}{V_LINE}
{V_LINE}{center_text('██║▄▄ ██║██║   ██║██╔══██║╚════██║██╔══██║██╔══██╗', 78)}{V_LINE}
{V_LINE}{center_text('╚██████╔╝╚██████╔╝██║  ██║███████║██║  ██║██║  ██║', 78)}{V_LINE}
{V_LINE}{center_text(' ╚══▀▀═╝  ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝', 78)}{V_LINE}
{V_LINE}{' ' * 78}{V_LINE}
{CORNER_BL}{H_LINE * 78}{CORNER_BR}
"""
    print(header)
    log_message("Displayed main header")

# --- СИСТЕМНЫЕ ФУНКЦИИ ---
def run_command(cmd, exit_on_error=True, show_progress=False):
    """Выполняет команду с возможным отображением прогресса"""
    log_message(f"Executing: {cmd}")
    try:
        if show_progress:
            # Создаем анимированный прогресс
            print(center_text(f"{next(SPINNER)} Выполнение: {cmd}", 80))
            
            process = subprocess.Popen(
                cmd, 
                shell=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True
            )
            
            # Анимация выполнения
            output_lines = []
            while process.poll() is None:
                line = process.stdout.readline()
                if line:
                    output_lines.append(line.strip())
                    print(f"\r{next(SPINNER)}", end='', flush=True)
                time.sleep(0.1)
            
            # Получаем оставшийся вывод
            remaining = process.stdout.read()
            if remaining:
                output_lines.append(remaining.strip())
            
            output = "\n".join(output_lines)
            error = process.stderr.read()
            
            print("\r✓", end='', flush=True)
            time.sleep(0.3)
            print("\n")
            
            log_command(cmd, output, error)
            return output
        else:
            result = subprocess.run(
                cmd, 
                shell=True, 
                check=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True
            )
            log_command(cmd, result.stdout, result.stderr)
            return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        log_message(f"Command failed: {cmd}")
        log_message(f"Error code: {e.returncode}")
        log_message(f"Error message: {e.stderr.strip()}")
        
        print(f"\nОшибка выполнения команды: {cmd}")
        print(f"Код ошибки: {e.returncode}")
        print(f"Сообщение: {e.stderr.strip()}")
        if exit_on_error:
            sys.exit(1)
        return None

def progress_bar(iteration, total, length=50):
    """Отображает текстовый прогресс-бар"""
    percent = ("{0:.1f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = '█' * filled_length + '-' * (length - filled_length)
    return f"|{bar}| {percent}%"

def check_disk_type(disk):
    """Определяет тип диска (SSD/HDD) и выдает предупреждение"""
    try:
        disk_name = os.path.basename(disk)
        with open(f'/sys/block/{disk_name}/queue/rotational', 'r') as f:
            rotational = int(f.read().strip())
        
        if rotational == 1:
            return "HDD (механический)"
        else:
            return "SSD (твердотельный)"
    except Exception as e:
        return "Неизвестный"

def get_disks():
    """Возвращает список доступных дисков"""
    disks = []
    output = run_command("lsblk -d -o NAME,SIZE,MODEL,TYPE -n")
    for line in output.split('\n'):
        if line:
            parts = line.split()
            if len(parts) >= 3:
                disk = {
                    'name': parts[0],
                    'size': parts[1],
                    'model': ' '.join(parts[2:-1]),
                    'type': parts[-1]
                }
                disks.append(disk)
    return disks

def select_disk(disks):
    """Отображает меню выбора диска"""
    while True:
        print_header()
        content = [
            f"{d['name']:6} {d['size']:8} {d['model'][:40]:40} {d['type']}" 
            for d in disks
        ]
        print(draw_box("ДОСТУПНЫЕ ДИСКИ", width=80, content=content))
        
        choice = input("\n" + center_text("Введите имя диска (например, sda, nvme0n1): ", 80)).strip()
        disk_path = f"/dev/{choice}"
        
        if os.path.exists(disk_path):
            # Проверяем тип диска
            disk_type = check_disk_type(disk_path)
            log_message(f"Selected disk: {disk_path} ({disk_type})")
            if "HDD" in disk_type:
                print_header()
                print(draw_box(
                    "ВНИМАНИЕ: МЕДЛЕННЫЙ ДИСК", 
                    width=80, 
                    content=[
                        "Обнаружен механический жесткий диск (HDD)!",
                        "Производительность системы будет ОЧЕНЬ НИЗКОЙ!",
                        "Рекомендуется использовать SSD для нормальной работы.",
                        "",
                        "Вы действительно хотите продолжить установку на HDD?"
                    ],
                    footer="Введите 'y' для подтверждения или 'n' для отмены"
                ))
                
                confirm = input(center_text("Ваш выбор (y/N): ", 80)).strip().lower()
                if confirm != 'y':
                    continue
            return disk_path
        else:
            print(center_text(f"Диск {disk_path} не существует!", 80))
            log_message(f"Invalid disk selected: {disk_path}")
            time.sleep(2)

def partition_disk(disk):
    """Выполняет разметку диска с помощью cfdisk"""
    print_header()
    print(draw_box(
        "РАЗМЕТКА ДИСКА", 
        width=80, 
        content=[
            f"Будет запущен cfdisk для диска: {disk}",
            "",
            "Инструкция:",
            "1. Создайте необходимые разделы",
            "2. Установите правильные типы разделов",
            "3. Сохраните изменения и выйдите"
        ],
        footer="Нажмите Enter для запуска cfdisk..."
    ))
    input()
    
    os.system(f"cfdisk {disk}")
    log_message(f"Partitioned disk: {disk}")
    
    # Показываем результат разметки
    print_header()
    print(center_text("РЕЗУЛЬТАТ РАЗМЕТКИ", 80))
    partition_info = run_command(f"fdisk -l {disk} | grep '^/'")
    print(partition_info)
    log_message(f"Partition info:\n{partition_info}")
    print("\n" + center_text("Разметка завершена. Нажмите Enter для продолжения...", 80))
    input()

def format_partitions(uefi_mode, root_part, boot_part):
    """Форматирует разделы"""
    print_header()
    print(draw_box(
        "ФОРМАТИРОВАНИЕ РАЗДЕЛОВ", 
        width=80, 
        content=[
            f"Корневой раздел: {root_part} -> ext4",
            f"Загрузочный раздел: {boot_part} -> {'FAT32' if uefi_mode else 'ext4'}",
            "",
            "Выполняется форматирование..."
        ]
    ))
    
    # Форматирование с прогрессом
    if uefi_mode:
        run_command(f"mkfs.fat -F32 {boot_part}", show_progress=True)
    else:
        run_command(f"mkfs.ext4 -F {boot_part}", show_progress=True)
    
    run_command(f"mkfs.ext4 -F {root_part}", show_progress=True)
    
    print(center_text("✓ Форматирование завершено!", 80))
    time.sleep(1)
    log_message("Partitions formatted successfully")

def mount_partitions(uefi_mode, root_part, boot_part):
    """Монтирует разделы"""
    print_header()
    print(draw_box(
        "МОНТИРОВАНИЕ РАЗДЕЛОВ", 
        width=80, 
        content=[
            f"Монтирование корневого раздела: {root_part} -> /mnt",
            f"Монтирование загрузочного раздела: {boot_part} -> {'/mnt/boot/efi' if uefi_mode else '/mnt/boot'}",
            "",
            "Выполняется монтирование..."
        ]
    ))
    
    run_command(f"mount {root_part} /mnt", show_progress=True)
    
    if uefi_mode:
        os.makedirs("/mnt/boot/efi", exist_ok=True)
        run_command(f"mount {boot_part} /mnt/boot/efi", show_progress=True)
    else:
        os.makedirs("/mnt/boot", exist_ok=True)
        run_command(f"mount {boot_part} /mnt/boot", show_progress=True)
    
    print(center_text("✓ Монтирование завершено!", 80))
    time.sleep(1)
    log_message("Partitions mounted successfully")

def set_password(username, is_root=False):
    """Устанавливает пароль для пользователя с подтверждением"""
    while True:
        print_header()
        prompt = f"Установка пароля для {'ROOT' if is_root else username}"
        print(draw_box(
            prompt,
            width=60,
            content=[
                "Введите пароль:",
                "(пароль не будет отображаться при вводе)"
            ]
        ))
        
        password1 = getpass("")
        
        print(draw_box(
            prompt,
            width=60,
            content=[
                "Повторите пароль:",
                "(для подтверждения)"
            ]
        ))
        password2 = getpass("")
        
        if password1 == password2:
            if is_root:
                run_command(f"echo 'root:{password1}' | artix-chroot /mnt chpasswd", show_progress=True)
            else:
                run_command(f"echo '{username}:{password1}' | artix-chroot /mnt chpasswd", show_progress=True)
            log_message(f"Password set for {'root' if is_root else username}")
            return
        else:
            print(center_text("Пароли не совпадают! Попробуйте снова.", 80))
            time.sleep(2)

def install_base_system(username, uefi_mode, disk, boot_part):
    """Устанавливает базовую систему"""
    print_header()
    content = [
        "Установка базовой системы с runit...",
        "",
        "Пакеты:",
        "base base-devel runit dbus-runit elogind-runit",
        "dhcpcd linux-zen plasma-nm linux-zen-headers dkms dbus sudo",
        "grub os-prober efibootmgr networkmanager-runit fish mc htop",
        "wget curl git iwd terminus-font"
    ]
    print(draw_box("УСТАНОВКА СИСТЕМЫ", width=90, content=content))
    
    # Установка пакетов с прогресс-баром
    packages = " ".join([
        "base", "base-devel", "runit", "dbus-runit", "elogind-runit",
        "dhcpcd", "linux-zen", "plasma-nm", "linux-zen-headers", "dkms", "dbus", "sudo",
        "grub", "os-prober", "efibootmgr", "networkmanager-runit", "fish", "mc", "htop",
        "wget", "curl", "git", "iwd", "terminus-font"
    ])
    
    print(center_text("Идет установка пакетов...", 80))
    run_command(f"basestrap /mnt {packages}", show_progress=True)
    
    # Настройка fstab
    print(center_text("Генерация fstab...", 80))
    run_command("fstabgen -U /mnt >> /mnt/etc/fstab", show_progress=True)
    run_command("cp /etc/pacman.conf /mnt/etc/", show_progress=True)
    
    # Создание пользователя
    print(center_text(f"Создание пользователя {username}...", 80))
    run_command(f"artix-chroot /mnt useradd -m -G wheel -s /bin/bash {username}", show_progress=True)
    run_command(f"artix-chroot /mnt usermod -aG audio,video,input,storage,optical,lp,scanner {username}")
    
    # Установка паролей
    set_password(username, is_root=False)
    set_password(username, is_root=True)
    
    # Копирование файлов
    print(center_text("Копирование системных файлов...", 80))
    try:
        # Копируем из директории установщика
        shutil.copytree(os.path.join(INSTALLER_DIR, "pixmap"), 
                       "/mnt/usr/share/pixmap", 
                       dirs_exist_ok=True)
        
        # Копируем скрипты установки
        for script in ["INSTALL.sh", "INST.sh"]:
            src = os.path.join(INSTALLER_DIR, script)
            if os.path.exists(src):
                shutil.copy(src, f"/mnt/home/{username}/")
                run_command(f"chown {username}:{username} /mnt/home/{username}/{script}")
                run_command(f"chmod +x /mnt/home/{username}/{script}")
                log_message(f"Copied {script} to /mnt/home/{username}/")
        
        # Копируем systemctl
        systemctl_src = os.path.join(INSTALLER_DIR, "systemctl")
        if os.path.exists(systemctl_src):
            shutil.copy(systemctl_src, "/mnt/usr/local/bin/")
            os.chmod("/mnt/usr/local/bin/systemctl", 0o755)
            log_message("Copied systemctl to /mnt/usr/local/bin/")
    except Exception as e:
        log_message(f"Error copying files: {str(e)}")
        print(center_text(f"Ошибка копирования файлов: {e}", 80))
        time.sleep(2)
    
    # Настройка chroot
    setup_chroot(username, uefi_mode, disk, boot_part)
    
    # Финализация
    print_header()
    print(draw_box(
        "УСТАНОВКА ЗАВЕРШЕНА", 
        width=80, 
        content=[
            "Базовая система успешно установлена!",
            "",
            "Дальнейшие шаги:",
            f"1. Перезагрузите систему",
            f"2. Войдите как пользователь {username}",
            f"3. Запустите скрипт INST.sh для установки KDE Plasma"
        ],
        footer="Нажмите Enter для выхода..."
    ))
    input()
    log_message("Base system installation completed")

def setup_chroot(username, uefi_mode, disk, boot_part):
    """Выполняет настройку внутри chroot"""
    chroot_script = f"""#!/bin/bash
# Настройка времени
ln -sf /usr/share/zoneinfo/Europe/Moscow /etc/localtime
hwclock --systohc

# Локализация
echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen
echo "ru_RU.UTF-8 UTF-8" >> /etc/locale.gen
locale-gen
echo "LANG=ru_RU.UTF-8" > /etc/locale.conf

# Сеть
echo "quasarlinux" > /etc/hostname
cat > /etc/hosts << EOF
127.0.0.1 localhost
::1 localhost
127.0.1.1 quasarlinux.localdomain quasarlinux
EOF

# Ребрендинг
cat > /etc/os-release << EOF
NAME="Quasar Linux"
PRETTY_NAME="Quasar Linux (Artix base)"
ID=quasar
ID_LIKE=artix
ANACONDA_ID="quasar"
VERSION="1.0"
VERSION_ID="1.0"
BUILD_ID="rolling"
ANSI_COLOR="0;36"
HOME_URL="https://b-e-n-z1342.github.io"
LOGO=quasar-logo
EOF

# Загрузчик GRUB
if [ {uefi_mode} -eq 1 ]; then
    grub-install --target=x86_64-efi --efi-directory=/boot/efi --bootloader-id=GRUB --recheck
else:
    grub-install --target=i386-pc {disk} --recheck
fi

sed -i 's/GRUB_DISTRIBUTOR=.*/GRUB_DISTRIBUTOR="Quasar Linux"/' /etc/default/grub
grub-mkconfig -o /boot/grub/grub.cfg

# Активация сервисов runit
ln -sf /etc/runit/sv/dbus /run/runit/service/
ln -sf /etc/runit/sv/elogind /run/runit/service/
ln -sf /etc/runit/sv/acpid /run/runit/service/
ln -sf /etc/runit/sv/NetworkManager /run/runit/service/

# Создание .bashrc
cat >> /home/{username}/.bashrc << EOF
if [ ! -f ~/.Quasar_post_done ]; then
    ./INST.sh
    touch ~/.Quasar_post_done
fi
EOF
"""
    
    # Сохраняем и выполняем скрипт
    with open("/mnt/chroot_setup.sh", "w") as f:
        f.write(chroot_script)
    
    os.chmod("/mnt/chroot_setup.sh", 0o755)
    print(center_text("Настройка chroot-окружения...", 80))
    run_command("artix-chroot /mnt /chroot_setup.sh", show_progress=True)
    os.remove("/mnt/chroot_setup.sh")
    log_message("Chroot setup completed")

def main():
    # Инициализация логов
    log_init()
    
    # Проверка прав
    if os.geteuid() != 0:
        print(center_text("Этот скрипт должен запускаться с правами root!", 80))
        log_message("Script started without root privileges!")
        sys.exit(1)
    
    log_message("Installer started with root privileges")
    
    # Проверка режима загрузки
    uefi_mode = os.path.exists("/sys/firmware/efi")
    boot_mode = "UEFI" if uefi_mode else "BIOS"
    log_message(f"Boot mode detected: {boot_mode}")
    
    # Установка шрифта
    run_command("pacman -Sy terminus-font --noconfirm", show_progress=True)
    run_command("setfont ter-v20n")
    
    print_header()
    print(draw_box(
        "РЕЖИМ ЗАГРУЗКИ", 
        width=60, 
        content=[f"Обнаружен режим загрузки: {boot_mode}"],
        footer="Нажмите Enter для продолжения..."
    ))
    input()
    
    # Выбор диска
    disks = get_disks()
    disk = select_disk(disks)
    
    # Разметка диска
    partition_disk(disk)
    
    # Выбор разделов
    print_header()
    print(center_text("СПИСОК РАЗДЕЛОВ", 80))
    partition_info = run_command(f"fdisk -l {disk} | grep '^/'")
    print(partition_info)
    log_message(f"Partition info:\n{partition_info}")
    
    print("\n")
    root_part = input(center_text("Введите раздел для ROOT (например, /dev/sda2): ", 80)).strip()
    boot_part = input(center_text("Введите раздел для BOOT/EFI (например, /dev/sda1): ", 80)).strip()
    log_message(f"Selected partitions: ROOT={root_part}, BOOT/EFI={boot_part}")
    
    # Форматирование
    format_partitions(uefi_mode, root_part, boot_part)
    
    # Монтирование
    mount_partitions(uefi_mode, root_part, boot_part)
    
    # Создание пользователя
    print_header()
    username = input(center_text("Введите имя нового пользователя: ", 80)).strip()
    log_message(f"Creating user: {username}")
    
    # Установка системы
    install_base_system(username, uefi_mode, disk, boot_part)
    
    # Очистка
    print(center_text("Завершение установки...", 80))
    run_command("umount -R /mnt", exit_on_error=False, show_progress=True)
    print(center_text("✓ Установка завершена! Перезагрузите систему.", 80))
    log_message("Installation completed successfully")

if __name__ == "__main__":
    main()
