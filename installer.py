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
import fcntl
import struct
import select
from getpass import getpass
from itertools import cycle

# --- КОНФИГУРАЦИЯ ---
LOG_DIR = "/Quasar--installer"
LOG_FILE = f"{LOG_DIR}/install.log"
INSTALLER_DIR = os.path.dirname(os.path.abspath(__file__))

# Создаем директорию для логов
os.makedirs(LOG_DIR, exist_ok=True)

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

# --- УТИЛИТЫ ТЕРМИНАЛА ---
def get_terminal_size():
    """Получаем размер терминала"""
    try:
        h, w, _, _ = struct.unpack('HHHH', 
            fcntl.ioctl(0, termios.TIOCGWINSZ, 
            struct.pack('HHHH', 0, 0, 0, 0)))
        return w, h
    except:
        return 80, 24  # Стандартный размер

# --- ПРОГРЕСС-БАРЫ ---
class ProgressBar:
    def __init__(self, total, description="", width=50):
        self.total = total
        self.description = description
        self.width = width
        self.current = 0
        self.start_time = time.time()
        
    def update(self, value):
        """Обновляем прогресс"""
        self.current = value
        self.draw()
        
    def increment(self, delta=1):
        """Увеличиваем прогресс"""
        self.current += delta
        self.draw()
        
    def draw(self):
        """Рисуем прогресс-бар"""
        percent = self.current / self.total
        filled = int(self.width * percent)
        bar = '█' * filled + '-' * (self.width - filled)
        elapsed = time.time() - self.start_time
        
        # Расчет оставшегося времени
        if percent > 0:
            remaining = (elapsed / percent) * (1 - percent)
            time_str = f"{remaining:.1f}s"
        else:
            time_str = "???"
            
        # Центрирование
        term_width, _ = get_terminal_size()
        desc_width = term_width - self.width - 20
        desc = (self.description[:desc_width] + '..') if len(self.description) > desc_width else self.description
        
        # Форматированная строка
        progress_str = f"\r{desc.ljust(desc_width)} |{bar}| {percent*100:.1f}% [{self.current}/{self.total}] ⏱{time_str}"
        sys.stdout.write(progress_str)
        sys.stdout.flush()
        
    def complete(self):
        """Завершаем прогресс-бар"""
        self.update(self.total)
        print()

# --- ИНТЕРФЕЙСНЫЕ ФУНКЦИИ ---
def clear_screen():
    os.system('clear')

def draw_box(title, content=None, footer=None):
    """Рисует красивый центрированный блок"""
    term_width, _ = get_terminal_size()
    width = min(term_width - 4, 100)
    
    # Верхняя граница
    box = "┌" + "─" * (width - 2) + "┐\n"
    
    # Заголовок
    title_line = "│" + title.center(width - 2) + "│\n"
    box += title_line
    box += "├" + "─" * (width - 2) + "┤\n"
    
    # Контент
    if content:
        if isinstance(content, str):
            content = [content]
            
        for line in content:
            if len(line) > width - 4:
                # Перенос длинных строк
                parts = [line[i:i+width-4] for i in range(0, len(line), width-4)]
                for part in parts:
                    box += "│ " + part.ljust(width - 4) + " │\n"
            else:
                box += "│ " + line.ljust(width - 4) + " │\n"
    
    # Нижняя граница
    if footer:
        box += "├" + "─" * (width - 2) + "┤\n"
        if len(footer) > width - 4:
            footer_parts = [footer[i:i+width-4] for i in range(0, len(footer), width-4)]
            for part in footer_parts:
                box += "│ " + part.center(width - 4) + " │\n"
        else:
            box += "│ " + footer.center(width - 4) + " │\n"
    
    box += "└" + "─" * (width - 2) + "┘"
    return box

def print_header():
    clear_screen()
    term_width, _ = get_terminal_size()
    width = min(term_width - 4, 100)
    
    header = f"""
┌{"─" * (width - 2)}┐
│{" " * (width - 2)}│
│{"Quasar Linux Installer".center(width - 2)}│
│{" " * (width - 2)}│
│{"██████╗ ██╗   ██╗ █████╗ ███████╗ █████╗ ██████╗".center(width - 2)}│
│{"██╔═══██╗██║   ██║██╔══██╗██╔════╝██╔══██╗██╔══██╗".center(width - 2)}│
│{"██║   ██║██║   ██║███████║███████╗███████║██████╔╝".center(width - 2)}│
│{"██║▄▄ ██║██║   ██║██╔══██║╚════██║██╔══██║██╔══██╗".center(width - 2)}│
│{"╚██████╔╝╚██████╔╝██║  ██║███████║██║  ██║██║  ██║".center(width - 2)}│
│{" ╚══▀▀═╝  ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝".center(width - 2)}│
│{" " * (width - 2)}│
└{"─" * (width - 2)}┘
"""
    print(header)
    log_message("Displayed main header")

# --- СИСТЕМНЫЕ ФУНКЦИИ ---
def run_command(cmd, exit_on_error=True, show_progress=False, progress_desc=""):
    """Выполняет команду с возможным отображением прогресса"""
    log_message(f"Executing: {cmd}")
    try:
        if show_progress:
            print(f"\n{progress_desc}")
            
            process = subprocess.Popen(
                cmd, 
                shell=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True
            )
            
            # Читаем вывод построчно
            while True:
                output_line = process.stdout.readline()
                if output_line == '' and process.poll() is not None:
                    break
                if output_line:
                    print(f"  {output_line.strip()}")
                
            # Обрабатываем ошибки
            error = process.stderr.read()
            if error:
                log_message(f"Command error: {error}")
                print(f"  ERROR: {error.strip()}")
            
            returncode = process.poll()
            if returncode != 0:
                raise subprocess.CalledProcessError(returncode, cmd)
                
            return ""
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

def install_packages(packages, desc="Установка пакетов"):
    """Устанавливает пакеты с прогресс-баром"""
    print(f"\n{desc}:")
    total = len(packages)
    progress = ProgressBar(total, desc, width=40)
    
    for i, pkg in enumerate(packages):
        progress.update(i)
        run_command(f"pacman -S --noconfirm {pkg}", show_progress=False)
        time.sleep(0.1)  # Для плавности прогресса
        
    progress.complete()

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
        content = [f"{d['name']:6} {d['size']:8} {d['model'][:40]:40} {d['type']}" for d in disks]
        print(draw_box("ДОСТУПНЫЕ ДИСКИ", content=content))
        
        choice = input("\nВведите имя диска (например, sda, nvme0n1): ").strip()
        disk_path = f"/dev/{choice}"
        
        if os.path.exists(disk_path):
            disk_type = check_disk_type(disk_path)
            log_message(f"Selected disk: {disk_path} ({disk_type})")
            if "HDD" in disk_type:
                print_header()
                print(draw_box(
                    "ВНИМАНИЕ: МЕДЛЕННЫЙ ДИСК", 
                    content=[
                        "Обнаружен механический жесткий диск (HDD)!",
                        "Производительность системы будет ОЧЕНЬ НИЗКОЙ!",
                        "Рекомендуется использовать SSD для нормальной работы.",
                        "",
                        "Вы действительно хотите продолжить установку на HDD?"
                    ],
                    footer="Введите 'y' для подтверждения или 'n' для отмены"
                ))
                
                confirm = input("Ваш выбор (y/N): ").strip().lower()
                if confirm != 'y':
                    continue
            return disk_path
        else:
            print(f"Диск {disk_path} не существует!")
            log_message(f"Invalid disk selected: {disk_path}")
            time.sleep(2)

def partition_disk(disk):
    """Выполняет разметку диска с помощью cfdisk"""
    print_header()
    print(draw_box(
        "РАЗМЕТКА ДИСКА", 
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
    print("РЕЗУЛЬТАТ РАЗМЕТКИ:")
    partition_info = run_command(f"fdisk -l {disk} | grep '^/'")
    print(partition_info)
    log_message(f"Partition info:\n{partition_info}")
    print("\nРазметка завершена. Нажмите Enter для продолжения...")
    input()

def format_partitions(uefi_mode, root_part, boot_part):
    """Форматирует разделы"""
    print_header()
    print(draw_box(
        "ФОРМАТИРОВАНИЕ РАЗДЕЛОВ", 
        content=[
            f"Корневой раздел: {root_part} -> ext4",
            f"Загрузочный раздел: {boot_part} -> {'FAT32' if uefi_mode else 'ext4'}",
            "",
            "Выполняется форматирование..."
        ]
    ))
    
    # Форматирование
    if uefi_mode:
        run_command(f"mkfs.fat -F32 {boot_part}", progress_desc="Форматирование EFI раздела")
    else:
        run_command(f"mkfs.ext4 -F {boot_part}", progress_desc="Форматирование BOOT раздела")
    
    run_command(f"mkfs.ext4 -F {root_part}", progress_desc="Форматирование ROOT раздела")
    
    print("✓ Форматирование завершено!")
    time.sleep(1)
    log_message("Partitions formatted successfully")

def mount_partitions(uefi_mode, root_part, boot_part):
    """Монтирует разделы"""
    print_header()
    print(draw_box(
        "МОНТИРОВАНИЕ РАЗДЕЛОВ", 
        content=[
            f"Монтирование корневого раздела: {root_part} -> /mnt",
            f"Монтирование загрузочного раздела: {boot_part} -> {'/mnt/boot/efi' if uefi_mode else '/mnt/boot'}",
            "",
            "Выполняется монтирование..."
        ]
    ))
    
    run_command(f"mount {root_part} /mnt", progress_desc="Монтирование корневого раздела")
    
    if uefi_mode:
        os.makedirs("/mnt/boot/efi", exist_ok=True)
        run_command(f"mount {boot_part} /mnt/boot/efi", progress_desc="Монтирование EFI раздела")
    else:
        os.makedirs("/mnt/boot", exist_ok=True)
        run_command(f"mount {boot_part} /mnt/boot", progress_desc="Монтирование BOOT раздела")
    
    print("✓ Монтирование завершено!")
    time.sleep(1)
    log_message("Partitions mounted successfully")

def set_password(username, is_root=False):
    """Устанавливает пароль для пользователя с подтверждением"""
    while True:
        print_header()
        prompt = f"Установка пароля для {'ROOT' if is_root else username}"
        print(draw_box(
            prompt,
            content=[
                "Введите пароль:",
                "(пароль не будет отображаться при вводе)"
            ]
        ))
        
        password1 = getpass("")
        
        print(draw_box(
            prompt,
            content=[
                "Повторите пароль:",
                "(для подтверждения)"
            ]
        ))
        password2 = getpass("")
        
        if password1 == password2:
            if is_root:
                run_command(f"echo 'root:{password1}' | artix-chroot /mnt chpasswd")
            else:
                run_command(f"echo '{username}:{password1}' | artix-chroot /mnt chpasswd")
            log_message(f"Password set for {'root' if is_root else username}")
            return
        else:
            print("Пароли не совпадают! Попробуйте снова.")
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
    print(draw_box("УСТАНОВКА СИСТЕМЫ", content=content))
    
    # Установка пакетов с прогресс-баром
    packages = [
        "base", "base-devel", "runit", "dbus-runit", "elogind-runit",
        "dhcpcd", "linux-zen", "plasma-nm", "linux-zen-headers", "dkms", "dbus", "sudo",
        "grub", "os-prober", "efibootmgr", "networkmanager-runit", "fish", "mc", "htop",
        "wget", "curl", "git", "iwd", "terminus-font"
    ]
    
    install_packages(packages, "Установка системных пакетов")
    
    # Настройка fstab
    print("Генерация fstab...")
    run_command("fstabgen -U /mnt >> /mnt/etc/fstab", progress_desc="Создание fstab")
    run_command("cp /etc/pacman.conf /mnt/etc/", progress_desc="Копирование pacman.conf")
    
    # Создание пользователя
    print(f"Создание пользователя {username}...")
    run_command(f"artix-chroot /mnt useradd -m -G wheel -s /bin/bash {username}", progress_desc="Создание пользователя")
    run_command(f"artix-chroot /mnt usermod -aG audio,video,input,storage,optical,lp,scanner {username}")
    
    # Установка паролей
    set_password(username, is_root=False)
    set_password(username, is_root=True)
    
    # Копирование файлов
    print("Копирование системных файлов...")
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
        print(f"Ошибка копирования файлов: {e}")
        time.sleep(2)
    
    # Настройка chroot
    setup_chroot(username, uefi_mode, disk, boot_part)
    
    # Финализация
    print_header()
    print(draw_box(
        "УСТАНОВКА ЗАВЕРШЕНА", 
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

# Установка загрузчика GRUB с проверкой
if [ {uefi_mode} -eq 1 ]; then
    echo "Установка GRUB для UEFI..."
    # Создаем каталог для GRUB
    mkdir -p /boot/efi/EFI/GRUB
    
    # Устанавливаем GRUB
    grub-install --target=x86_64-efi --efi-directory=/boot/efi --bootloader-id=GRUB --recheck
    
    # Проверка установки
    if [ ! -f /boot/efi/EFI/GRUB/grubx64.efi ]; then
        echo "ОШИБКА: GRUB не установился!"
        exit 1
    fi
else
    echo "Установка GRUB для BIOS..."
    grub-install --target=i386-pc {disk} --recheck
fi

# Генерация конфигурации GRUB
echo "Генерация конфига GRUB..."
sed -i 's/GRUB_DISTRIBUTOR=.*/GRUB_DISTRIBUTOR="Quasar Linux"/' /etc/default/grub
grub-mkconfig -o /boot/grub/grub.cfg

# Проверка конфигурации
if [ ! -f /boot/grub/grub.cfg ]; then
    echo "ОШИБКА: Конфиг GRUB не создан!"
    exit 1
fi

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
    print("Настройка chroot-окружения...")
    run_command("artix-chroot /mnt /chroot_setup.sh", progress_desc="Выполнение chroot-скрипта")
    os.remove("/mnt/chroot_setup.sh")
    log_message("Chroot setup completed")

def main():
    # Инициализация логов
    log_init()
    
    # Проверка прав
    if os.geteuid() != 0:
        print("Этот скрипт должен запускаться с правами root!")
        log_message("Script started without root privileges!")
        sys.exit(1)
    
    log_message("Installer started with root privileges")
    
    # Проверка режима загрузки
    uefi_mode = os.path.exists("/sys/firmware/efi")
    boot_mode = "UEFI" if uefi_mode else "BIOS"
    log_message(f"Boot mode detected: {boot_mode}")
    
    # Установка шрифта
    run_command("pacman -Sy terminus-font --noconfirm", progress_desc="Установка шрифтов")
    run_command("setfont ter-v20n")
    
    print_header()
    print(draw_box(
        "РЕЖИМ ЗАГРУЗКИ", 
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
    print("СПИСОК РАЗДЕЛОВ:")
    partition_info = run_command(f"fdisk -l {disk} | grep '^/'")
    print(partition_info)
    log_message(f"Partition info:\n{partition_info}")
    
    print("\n")
    root_part = input("Введите раздел для ROOT (например, /dev/sda2): ").strip()
    boot_part = input("Введите раздел для BOOT/EFI (например, /dev/sda1): ").strip()
    log_message(f"Selected partitions: ROOT={root_part}, BOOT/EFI={boot_part}")
    
    # Форматирование
    format_partitions(uefi_mode, root_part, boot_part)
    
    # Монтирование
    mount_partitions(uefi_mode, root_part, boot_part)
    
    # Создание пользователя
    print_header()
    username = input("Введите имя нового пользователя: ").strip()
    log_message(f"Creating user: {username}")
    
    # Установка системы
    install_base_system(username, uefi_mode, disk, boot_part)
    
    # Очистка
    print("Завершение установки...")
    run_command("umount -R /mnt", exit_on_error=False, progress_desc="Размонтирование разделов")
    print("✓ Установка завершена! Перезагрузите систему.")
    log_message("Installation completed successfully")

if __name__ == "__main__":
    main()
