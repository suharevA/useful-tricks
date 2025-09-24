import subprocess
from subprocess import Popen, PIPE


# dnf install cloud-utils-growpart gdisk -y
#
def get_disk_info():
    # Используем parted для получения размера диска
    command_size = f'parted /dev/sda print | grep "/dev/sda: "'
    # command_size = 'lsblk -no SIZE /dev/sda'
    # Используем gdisk для проверки наличия таблицы разделов GPT
    command_gpt = 'gdisk -l /dev/sda | grep "GPT: present"'

    try:
        process_size = Popen(command_size, shell=True, stdout=PIPE, universal_newlines=True)
        output_size, _ = process_size.communicate()
        process_gpt = Popen(command_gpt, shell=True, stdout=PIPE, universal_newlines=True)
        output_gpt, _ = process_gpt.communicate()
    except Exception as e:
        print(f"Ошибка выполнения команды: {e}")
        return None, None

    size = output_size.strip().replace(',', '.').split()[-1].strip("GB")
    is_gpt = output_gpt.strip() != ''

    if int(float(size)) >= 2048 and not is_gpt:
        raise ValueError("Диск слишком большой и не имеет таблицы разделов GPT")

    return size, is_gpt


def get_pvs():
    pvs_output = Popen(['pvs'], stdout=PIPE).communicate()[0]
    pvs_lines = pvs_output.decode().split('\n')
    pvs_header = pvs_lines[0].split()
    pvs_data = [line.split() for line in pvs_lines[1:] if line.strip()]
    return pvs_header, pvs_data


def get_filesystem_type(device):
    command = f"lsblk -no FSTYPE {device}"
    output = Popen(command, shell=True, stdout=PIPE, universal_newlines=True).communicate()[0]
    return output.strip()


def get_root_partition():
    command = "mount | grep 'on / '"
    output = Popen(command, shell=True, stdout=PIPE, universal_newlines=True).communicate()[0]
    root_device = output.split()[0]
    return root_device


def get_partition_number(device):
    pvs_header, pvs_data = get_pvs()
    for line in pvs_data:
        if line[0].startswith('/dev/sda'):
            print("диск c LVM /dev/sda")
            sd = '/dev/sda'
            command = f'lsblk -n -o NAME "{sd}" | grep -oE "[0-9]+" && echo 1 > /sys/block/sda/device/rescan'
            # command = f'lsblk -n -o NAME "{sd}" | grep -oE "[0-9]+"'
            output = Popen(command, shell=True, stdout=PIPE, universal_newlines=True).communicate()[0]
            output_list = output.strip().split("\n")
            last_element = output_list[-1]
            print("Номер последней партиции:", last_element)
            partitions = output.split()
            return last_element, sd
        else:
            raise ValueError("Unknown device")
    # print("Номер последней партиции:", last_element)
    return None


def expand_partition(device, partition_number):
    print(f"Расширение партиции {partition_number[1]} {partition_number[0]} ")
    
    command = f"growpart {partition_number[1]} {partition_number[0]}"
    subprocess.run(command, shell=True)


def expand_filesystem(device):
    filesystem_type = get_filesystem_type(device)

    print("Расширение файловой системы:", filesystem_type)
    if filesystem_type == "xfs":
        command = f"pvresize {root_partition_number[1]}{root_partition_number[0]}"
        command_ext = f"lvextend -r -l +100%FREE {get_root_partition()}"
        command_grow = f"xfs_growfs {get_root_partition()}"
    elif filesystem_type == "ext4":
        command = f"pvresize {root_partition_number[1]}{root_partition_number[0]}"
        command_ext = f"lvextend -r -l +100%FREE {get_root_partition()}"
        command_grow = f"resize2fs {get_root_partition()}"

    else:
        print("Unsupported filesystem type")
        return
    subprocess.run(command, shell=True)
    subprocess.run(command_ext, shell=True)
    subprocess.run(command_grow, shell=True)
    print(subprocess.run("lsblk", shell=True))


# Определение корневого раздела
get_disk_info()
root_device = get_root_partition()
print("ROOT:", root_device)
root_partition_number = get_partition_number(root_device)
if root_partition_number is not None:
    # Расширение раздела

    expand_partition(root_device, root_partition_number)

    # Расширение файловой системы или LVM
    if get_filesystem_type(root_device) == "xfs":
        expand_filesystem(root_device)
    else:
        expand_filesystem(root_device)
else:
    print("Failed to determine root partition")