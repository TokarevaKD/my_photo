from nicegui import ui
from datetime import datetime
from pathlib import Path
import shutil
import json
import os


UPLOAD_DIR = Path('uploads')
FAVORITES_FILE = Path('favorites.json')
COMMENTS_FILE = Path('comments.json')
METADATA_FILE = Path('metadata.json')

UPLOAD_DIR.mkdir(exist_ok=True)

# Загрузка и сохранение JSON-файлов
def load_json(file_path):
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_json(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# Данные приложения
favorites = load_json(FAVORITES_FILE)
comments = load_json(COMMENTS_FILE)
metadata = load_json(METADATA_FILE)

# UI логика
def save_metadata(filename):
    metadata[filename] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    save_json(METADATA_FILE, metadata)

def add_to_favorites(filename):
    favorites[filename] = True
    save_json(FAVORITES_FILE, favorites)

def remove_from_favorites(filename):
    favorites.pop(filename, None)
    save_json(FAVORITES_FILE, favorites)

def is_favorite(filename):
    return favorites.get(filename, False)

def set_comment(filename, text):
    comments[filename] = text
    save_json(COMMENTS_FILE, comments)

def get_comment(filename):
    return comments.get(filename, '')

def delete_photo(filename):
    try:
        os.remove(UPLOAD_DIR / filename)
        favorites.pop(filename, None)
        comments.pop(filename, None)
        metadata.pop(filename, None)
        save_json(FAVORITES_FILE, favorites)
        save_json(COMMENTS_FILE, comments)
        save_json(METADATA_FILE, metadata)
        ui.notify('Фото удалено')
        ui.run_javascript('location.reload()')
    except Exception as e:
        ui.notify(f'Ошибка удаления: {e}')

def show_photo_detail(filename):
    with ui.dialog().props('maximized') as dialog:
        with ui.column().classes('items-center justify-center').style('width: 100%'):
            # Фото
            ui.image(UPLOAD_DIR / filename).classes('w-1/2 mb-4 rounded-lg shadow-md')

            # Метадата
            ui.label(f'Загружено: {metadata.get(filename, "?")}') \
                .classes('bg-yellow-50 border border-yellow-300 rounded-md px-4 py-2 text-sm shadow-inner')

            # Красивое поле ввода комментария в карточке
            with ui.card().classes('w-1/2 p-4 bg-yellow-50 rounded-xl shadow'):
                ui.label('Комментарий').classes('text-md font-semibold mb-1')
                comment_area = ui.textarea(
                    value=get_comment(filename)
                ).classes('w-full h-16 rounded-md shadow-inner border border-yellow-300 px-3 py-2 text-base')


           

            # Нижняя панель с кнопками
            with ui.row().classes('justify-end w-full gap-2 mt-2 px-4'):
                ui.button('УДАЛИТЬ ФОТО', on_click=lambda: delete_photo(filename)).props('color=red')
                ui.button('СОХРАНИТЬ', on_click=lambda: set_comment(filename, comment_area.value)).props('color=primary')
                ui.button('ЗАКРЫТЬ', on_click=dialog.close).props('color=secondary')

        dialog.open()




def show_gallery(only_favorites=False):
    ui.label('Мой фотоальбом').classes('text-xl mt-4')
    with ui.row().classes('flex-wrap gap-6 justify-start'):
        for file in sorted(UPLOAD_DIR.iterdir(), reverse=True):
            if file.is_file() and file.suffix.lower() in ['.jpg', '.png', '.jpeg']:
                if only_favorites and not is_favorite(file.name):
                    continue
                file_name = file.name  
                with ui.column().classes('items-center'):
                    with ui.card().classes('w-[200px] h-[200px] p-2 cursor-pointer shadow-lg'):
                        ui.image(file).classes('object-cover w-full h-full rounded-md') \
                            .on('click', lambda e=None, f=file_name: show_photo_detail(f))

                    comment_text = get_comment(file_name)
                    if comment_text:
                        ui.label(comment_text).classes(
                            'text-base text-center font-bold text-white bg-black/60 p-1 rounded-md w-[160px]'
                        )





def upload_image(e):
    uploaded_file = e.name
    file_path = UPLOAD_DIR / uploaded_file
    with open(file_path, 'wb') as f:
        f.write(e.content.read())

    save_metadata(uploaded_file)
    ui.notify('Фото загружено')
    ui.run_javascript('location.reload()')

def open_upload_dialog():
    dialog = ui.dialog()
    with dialog:
        with ui.card():
            ui.label('Загрузить изображение')
            ui.upload(on_upload=upload_image, auto_upload=True).props('accept=image/*')
            ui.button('Закрыть', on_click=dialog.close).props('color=secondary')
    dialog.open()

def show_header():
    with ui.header().classes('items-center justify-between'):
        ui.button(icon='add', on_click=open_upload_dialog).props('flat color=black')
        ui.button('Избранное', on_click=lambda: ui.open('/favorites')).props('flat')
        ui.button('Все фото', on_click=lambda: ui.open('/')).props('flat')

@ui.page('/')
def main_page():
    show_header()
    show_gallery()



ui.add_body_html("""
<style>
body {
    background-image: url('/static/background.jpg');
    background-size: cover;
    background-attachment: fixed;
    background-position: center;
}
</style>
""")

ui.run(title='Мой Фотоальбом', reload=False, native=True, fullscreen=False)
