import subprocess
import argparse
import ast

def get_vg_name():
    try:
        # Выполнение команды 'lvs -o vg_name' и получение вывода
        result = subprocess.run(['lvs', '-o', 'vg_name', '--noheadings'], stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)

        # Проверка на ошибки во время выполнения команды
        if result.returncode != 0:
            # Вывод сообщения об ошибке, если она произошла
            print("Ошибка при выполнении команды:", result.stderr.decode('utf-8'))
            return None

        # Декодирование байтовой строки и получение имени группы томов без пробельных символов с начала и конца строки
        vg_names = result.stdout.decode('utf-8').strip().replace(' ', '')

        # Исключаем имена 'rhel' и 'vg_sys', разделяя строки и проверяя каждую
        vg_names_filtered = [name for name in vg_names.splitlines() if name not in ['rl', 'rhel', 'vg_sys']]
        return vg_names_filtered

    except FileNotFoundError:
        # Ошибка, если команда lvs не найдена
        print("Команда 'lvs' не найдена. Убедитесь, что у вас установлены LVM инструменты.")
        return None


def get_non_lvm_devices():
    # Выполняем команду lsblk для получения списка всех блочных устройств
    lsblk_output = subprocess.check_output(['lsblk', '-d', '-o', 'NAME']).decode('utf-8').strip().split('\n')
    # Выполняем команду pvs для получения списка всех физических томов LVM
    pvs_output = subprocess.check_output(['pvs', '-o', 'pv_name', '--no-heading']).decode('utf-8').strip().replace(' ',
                                                                                                                   '').split(
        '\n')

    # Инициализируем пустой список для дисков, не используемых в LVM
    non_lvm_devices = []

    # Проходим по каждому устройству
    for device in lsblk_output:
        try:
            # Проверяем, не входит ли устройство в список LVM устройств
            if f'/dev/{device}' not in pvs_output and device != 'sda' and device != 'sr0' and device != 'NAME':
                # Выполняем команду lsblk для получения размера диска
                disk_sizes = subprocess.check_output(['lsblk', '-n', f'/dev/{device}', '-d', '-o', 'SIZE']).decode(
                    'utf-8').strip().strip('G').split('\n')
                # Если устройство не в списке LVM и не является sda, добавляем его в список
                non_lvm_devices.append(f'{device, int(disk_sizes[0])}')
        except ValueError:
            disk_sizes = float(subprocess.check_output(['lsblk', '-n', f'/dev/{device}', '-d', '-o', 'SIZE']).decode(
                'utf-8').strip().strip('T'))
            disk_sizes = int(disk_sizes * 1024)
            non_lvm_devices.append(f'{device, disk_sizes}')

    # Возвращаем список дисков, не используемых в LVM
    return non_lvm_devices


def main():
    non_lvm_devices = get_non_lvm_devices()
    # print("Диски, не используемые в LVM (исключая sda):")
    for device in non_lvm_devices:
        return device


def check_volume_groups_and_disks():
    non_lvm_devices = get_non_lvm_devices()
    print("Диски, не используемые в LVM (исключая sda):")
    for device in non_lvm_devices:
        print(device)



def vg_resize(device, mount_point, vg_name, lv_name):
    """Resize LVM volume group and logical volume"""
    device_tuple = ast.literal_eval(device)
    subprocess.run(f"pvcreate /dev/{device_tuple[0]}", shell=True, check=True)
    subprocess.run(f"vgcreate {vg_name} /dev/{device_tuple[0]}", shell=True, check=True)
    subprocess.run(f"lvcreate -l 100%FREE -n {lv_name} {vg_name}", shell=True, check=True)

    # Создаем новую файловую систему
    subprocess.run(f"mkfs.xfs -f /dev/{vg_name}/{lv_name}", shell=True, check=True)
    subprocess.run(f"mkdir -p {mount_point}", shell=True, check=True)
    subprocess.run(f"mount /dev/{vg_name}/{lv_name} {mount_point}", shell=True, check=True)
    entry = f"/dev/{vg_name}/{lv_name} {mount_point} xfs defaults 0 0"
    with open('/etc/fstab', 'r') as fstab:
        for line in fstab:
            if not line.startswith('#') and entry in line:
                print("Запись уже существует в /etc/fstab.")
                return False  # Entry already exists, no need to append

    # If the entry does not exist, append it to /etc/fstab
    try:
        # Use subprocess.run with check=True to raise an exception if the command fails
        subprocess.run(f"echo '{entry}' | sudo tee -a /etc/fstab", shell=True, check=True)
        print("Запись добавлена в /etc/fstab.")
        return True  # Entry was appended
    except subprocess.CalledProcessError as e:
        print(f"Failed to append entry to /etc/fstab: {e}")
        return False  # Failed to append entry



def action():
    non_lvm_devices = get_non_lvm_devices()
    if parameters['current_size'] == 0:
        vg_names = get_vg_name()
        if not vg_names:
            print(f"Диски {non_lvm_devices}, не используемые в LVM (исключая sda):")
            for device in non_lvm_devices:
                device_size = int(device.strip("()").split()[1])
                if device_size == parameters['total_size']:
                    print(f"Текущий размер равен размеру диска {device}, создаю новую группу томов.")
                    vg_names = "vg_data_auto_1"
                    lv_name = "lv_data_auto_1"
                    vg_resize(device, parameters['mount_point'], vg_names, lv_name)
                    break
                else:

                    print(f"Размер диска {device} не соответствует текущему размеру.")

        else:
            print("Существующие volume группы найдены.", get_vg_name())
            base_vg_name = "vg_data_auto_"
            base_lv_name = "lv_data_auto_"
            counter = 1 if "vg_data_auto_1" in get_vg_name() else 0
            new_vg_name = f"{base_vg_name}{counter + 1}"
            new_lv_name = f"{base_lv_name}{counter + 1}"
            print(f"Создаю новую группу томов {new_vg_name}.")
            for device in non_lvm_devices:
                device_size = int(device.strip("()").split()[1])
                if device_size == parameters['total_size']:
                    vg_resize(device, parameters['mount_point'], new_vg_name, new_lv_name)
                    break
                else:

                    print(f"Размер диска {device} не соответствует текущему размеру.")

    else:
        if parameters['current_size'] != 0:
            print("Текущий размер не равен нулю, проверка не требуется.")
            print("Существующие volume группы найдены.", get_vg_name())

        size_tuple = ast.literal_eval(main())
        remaining_size = parameters['total_size'] - parameters['current_size']

        if size_tuple[-1] == remaining_size:
            print("Размеры дисков совпадают.")
            with open('/etc/fstab', 'r') as file:
                for line in file:
                    if not line.startswith('#') and parameters['mount_point'] in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            print(f"Найден подходящий диск {main()} и точка монтирования: {parts[0]}, {parts[1]}")
                            lvdisplay_output = subprocess.check_output(['lvdisplay', parts[0]]).decode(
                                'utf-8').strip().split('\n')
                            for line in lvdisplay_output:
                                if "VG Name" in line:
                                    vg_name = line.split()[-1]  # VG name is the third word in the line
                                    subprocess.run(f"vgextend {vg_name} /dev/{size_tuple[0]} && lvextend -r -l+100%free {parts[0]} && lsblk", shell=True, check=True)
                                    break
                        else:
                            print("Ничего не нашли.")
                            return (parts[0], parts[1])


        else:
            print("Размеры дисков не совпадают.")



if __name__ == "__main__":
    # Создаем парсер
    parser = argparse.ArgumentParser()
    # Определяем ожидаемые аргументы
    parser.add_argument('--current_size', type=int, required=True)
    parser.add_argument('--total_size', type=int, required=True)
    parser.add_argument('--mount_point', type=str, required=True)
    # parser.add_argument('--host', type=str, required=True)
    # Разбираем аргументы
    args = parser.parse_args()
    # Преобразуем в словарь
    parameters = vars(args)
    action()
