import os


def get_human_readable(size, precision=2):
    """Переводим в удобочитаемый вид"""
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB']
    suffixIndex = 0
    while size > 1024:
        suffixIndex += 1  # increment the index of the suffix
        size = size / 1024.0  # apply the division
    return "%.*f %s" % (precision, size, suffixes[suffixIndex])


def list_files(startpath):
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print('{}{}\\'.format(indent, os.path.basename(root)))
        subindent = ' ' * 4 * (level + 1)
        for f in sorted(files, key=lambda f: os.path.getsize(root + os.sep + f)):
            converted_size = get_human_readable(os.path.getsize(root + os.sep + f))
            print('{}{} - {}'.format(subindent, f, converted_size))
            with open("enum.txt", "a",  encoding='utf-8') as file:
                file.write('{}\{} - {}'.format(root, ' ' + f, converted_size) + "\n")


list_files(r'M:\Отдел Информационных Технологий')

