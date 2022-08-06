from PIL import Image, ImageDraw, ImageFont
import random
import os


def generate_img_list(folder_name):
    correct_photos = os.listdir(f'photos/{folder_name}/correct')
    wrong_photos = os.listdir(f'photos/{folder_name}/wrong')

    images = []
    images.append(Image.open(f'photos/{folder_name}/correct/{random.choice(correct_photos)}'))

    index = 0
    full_paths = []

    while True:
        photo = random.choice(wrong_photos)
        full_path = f'photos/{folder_name}/wrong/' + photo
        full_paths.append(images[index].filename)

        if full_path not in full_paths:
            images.append(Image.open(f'photos/{folder_name}/wrong/{photo}'))
            index += 1

        if index > 4:
            break

    random.shuffle(images)

    return images


def get_correct_img_index(images):
    for index, img in enumerate(images):
        if 'correct' in img.filename.split('/')[-1]:
            return index


def generate_final_img(images):
    img_width = 770
    img_height = 515
    margin_top = 5
    margin_left = 5

    main_img = Image.new('RGB', (img_width, img_height), color=('white'))

    for index, photo in enumerate(images):
        main_img.paste(photo, (margin_left, margin_top))
        margin_left += 255

        if index == 2:
            margin_left = 5
            margin_top = 260

    frame = Image.open('frame.png').convert("RGBA")
    main_img.paste(frame, (0, 0), frame)

    return main_img


def generate_verification_img():
    topic = random.choice(os.listdir('photos'))

    images = generate_img_list(topic)

    correct_img_index = get_correct_img_index(images)

    final_img = generate_final_img(images)

    return final_img, topic, correct_img_index
