import os
from PIL import Image
import pytesseract


def transfer_path(path):
    files_list = []
    for file in os.listdir(path):
        files_list.append(os.path.join(path, file))
    return files_list


def image2string(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image, lang='eng+chi_sim')
    return text.replace('\n', '').replace(' ', '')


def write2text(file_name, text_string):
    with open(file_name, 'a+') as fp:
        fp.write('%s\n' % text_string)


if __name__ == '__main__':
    path = 'F:\\Myself\\连环画\\2021-01-25\\商朝的故事 向日葵连环画'
    text_list = []
    for file_path in transfer_path(path):
        text = image2string(file_path)
        print(text)
        try:
            write2text('./商朝的故事.txt', text)
        except UnicodeEncodeError as e:
            continue





