# -*- coding: utf-8 -*-

import subprocess
import argparse
from decimal import Decimal
import re


# python3 script.py --current_size 0 --total_size 5000 --mount_point /data

def run_command(command):
    """Запуск команды и получение результата."""
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, check=True)
        return result.stdout.decode('utf-8').strip()
    except subprocess.CalledProcessError as e:
        print(command, e.stderr.decode('utf-8'))
        return None


def parse_size(size_str):
    """Конвертация строки размера в гигабайты с поддержкой дробных значений."""
    size_str = size_str.strip().replace(',', '.')
    try:
        if size_str.endswith('T'):
            return Decimal(size_str.strip('T')) * 1000
        elif size_str.endswith('G'):
            return Decimal(size_str.strip('G'))
        else:
            return Decimal('0')
    except Exception:
        return Decimal('0')


def size_matches(actual_size, expected_size, tolerance=0.1):
    """толерантность к размерам дисков (±10%)"""
    actual = Decimal(str(actual_size))
    expected = Decimal(str(expected_size))
    difference = abs(actual - expected)
    return difference <= (expected * Decimal(str(tolerance)))


def get_vg_name():
    output = run_command('lvs -o vg_name --noheadings')
    if output:
        vg_names = output.replace(' ', '').splitlines()
        return [name for name in vg_names if name not in ['rl', 'rhel', 'vg_sys', 'system-root']]
    return []


def check_disk_in_vg(disk_path):
    try:
        command = f"pvdisplay {disk_path}"
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        output_str = output.decode('utf-8')

        for line in output_str.split('\n'):
            if "VG Name" in line:
                vg_name = line.split("VG Name")[-1].strip()
                return vg_name if vg_name else None
        return None
    except subprocess.CalledProcessError:
        return None


def get_non_lvm_devices():
    lsblk_output = run_command('lsblk -d -o NAME,SIZE')
    pvs_output = run_command('pvs -o pv_name --no-heading')

    if not lsblk_output or not pvs_output:
        return []

    lvm_devices = pvs_output.replace(' ', '').splitlines()
    non_lvm_devices = []

    for line in lsblk_output.splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 2:
            device = parts[0]
            size_str = parts[1]
            print(f"Диск: {device}, Размер: {size_str}")

            if f'/dev/{device}' not in lvm_devices and device not in ['sda', 'sr0', 'fd0']:
                disk_path = f"/dev/{device}"
                vg_name = check_disk_in_vg(disk_path)

                if vg_name:
                    print(f"Диск {disk_path} принадлежит VG: {vg_name}")
                else:
                    print(f"Диск {disk_path} не принадлежит ни одному VG")
                    size_gb = parse_size(size_str)
                    if size_gb > 0:
                        non_lvm_devices.append((device, float(size_gb)))

    if not non_lvm_devices:
        print("Не найдены устройства без LVM")
    return non_lvm_devices


def vg_resize(device, mount_point, vg_name, lv_name):
    """Создание группы томов LVM и логического тома."""
    try:
        print(f"Найден подходящий диск {device} точка монтирования /dev/{vg_name}/{lv_name} {mount_point}")
        commands = [
            f"pvcreate /dev/{device}",
            f"vgcreate {vg_name} /dev/{device}",
            f"lvcreate -l 100%FREE -n {lv_name} {vg_name}",
            f"mkfs.xfs -f /dev/{vg_name}/{lv_name}",
            f"mkdir -p {mount_point}",
            f"mount /dev/{vg_name}/{lv_name} {mount_point}"
        ]

        for cmd in commands:
            result = run_command(cmd)

            if "A volume group called" in result and "already exists" in result:
                print(f"Группа томов {vg_name} уже существует. Прекращаем выполнение.")
                raise Exception(f"Ошибка при выполнении: {cmd}\nВывод: {result}")
            # if "error" in result.lower() or "failed" in result.lower():
            #     raise Exception(f"Ошибка при выполнении: {cmd}\nВывод: {result}")

        # Если выполнение дошло до этого момента, добавляем запись в fstab
        entry = f"/dev/{vg_name}/{lv_name} {mount_point} xfs defaults 0 0"
        with open('/etc/fstab', 'r') as fstab:
            if entry not in fstab.read():
                run_command(f"echo '{entry}' | sudo tee -a /etc/fstab")
                print("Запись добавлена в /etc/fstab.")
            else:
                print("Запись уже существует в /etc/fstab.")
    except Exception as e:
        raise Exception(f"Ошибка при создании LVM: {str(e)}")


def extend_vg_and_lv(device, mount_point):
    """Расширение группы томов LVM и логического тома."""
    try:
        with open('/etc/fstab', 'r') as file:
            for line in file:
                if not line.startswith('#') and mount_point in line:
                    parts = line.split()
                    if len(parts) >= 2 and parts[1] == mount_point:
                        vg_name = re.search(r'/dev/(\w+)/', parts[0])
                        if vg_name:
                            print(f"Найден подходящий диск {device} и точка монтирования: {parts[0]}, {parts[1]}")
                            print(f"Расширяю в группе томов {vg_name.group(1)}")
                            # print(f"lvdisplay {vg_name.group(1)}")
                            command = f"vgextend {vg_name.group(1)} /dev/{device} && lvextend -r -l+100%free {parts[0]}"
                            run_command(command)
                            return
                        # print(f"Найден подходящий диск {device} и точка монтирования: {parts[0]}, {parts[1]}")
                        # lvdisplay_output = run_command(f'lvdisplay {parts[0]}').split('\n')
                        # for lv_line in lvdisplay_output:
                        #     if "VG Name" in lv_line:
                        #         vg_name = lv_line.split()[-1]
                        #         command = f"vgextend {vg_name} /dev/{device} && lvextend -r -l+100%free {parts[0]}"
                        #         run_command(command)
                        #         return
        raise Exception("Не найдена подходящая точка монтирования.")
    except Exception as e:
        raise Exception(f"Ошибка при расширении LVM: {str(e)}")


def action(parameters):
    """Улучшенная логика обработки дисков."""
    non_lvm_devices = get_non_lvm_devices()
    current_size = Decimal(str(parameters['current_size']))
    total_size = Decimal(str(parameters['total_size']))

    if current_size == 0:
        # Создание нового тома
        for device, size in non_lvm_devices:
            if size_matches(size, total_size):
                try:
                    vg_names = get_vg_name()
                    vg_name = f"vg_data_auto_{len(vg_names) + 1}"
                    lv_name = f"lv_data_auto_{len(vg_names) + 1}"
                    vg_resize(device, parameters['mount_point'], vg_name, lv_name)
                    return
                except Exception as e:
                    print(f"Ошибка создания тома: {e}")
                    continue
    else:
        # Расширение существующего тома
        remaining_size = total_size - current_size
        for device, size in non_lvm_devices:
            if size_matches(size, remaining_size):
                try:
                    extend_vg_and_lv(device, parameters['mount_point'])
                    return
                except Exception as e:
                    print(f"Ошибка расширения тома: {e}")
                    continue

    raise Exception("Не найдено подходящих устройств")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Управление LVM томами")
    parser.add_argument('--current_size', type=int, required=True, help="Текущий размер в GB")
    parser.add_argument('--total_size', type=int, required=True, help="Требуемый общий размер в GB")
    parser.add_argument('--mount_point', type=str, required=True, help="Точка монтирования")

    args = parser.parse_args()
    try:
        action(vars(args))
    except Exception as e:
        print(f"Критическая ошибка: {str(e)}")
        exit(1)