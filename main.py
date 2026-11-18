"""Directory ZIP - フォルダをGUIでZIP圧縮するツール.

Flet を使ったデスクトップ GUI アプリ。
フォルダと保存先を選んでボタンを押すだけで ZIP 圧縮できる。

元の授業課題 (pyzip/dir_zip.py) をポートフォリオ用に整理したもの。
ロジックは元のまま、以下の点だけ修正している:
- zip_upload_path の text_align に数値 (14) が入っていたバグを修正
- 未選択時の案内文の重複を修正
- このファイル単体でも `python main.py` で起動できるよう入口を追加
"""

import asyncio
import os
import shutil

import flet as ft


def zip_exe():
    ft.run(main_frame)


def main_frame(page: ft.Page):
    page.window.resizable = False
    page.window.maximizable = False
    page.title = "Directory ZIP"

    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.window.width = 550
    page.window.height = 300
    page.window.top = 300
    page.window.left = 500

    zip_file_name = "zip.zip"

    directory_path = ft.TextField(
        label="圧縮したいフォルダ",
        text_align=ft.TextAlign.LEFT,
        height=60,
        width=470,
        text_size=14,
    )

    zip_upload_path = ft.TextField(
        label="圧縮先",
        height=60,
        width=470,
        text_align=ft.TextAlign.LEFT,
    )

    progress = ft.ProgressRing(
        visible=False,
        width=25,
        height=25,
    )

    zip_button = ft.Button(content="圧縮開始")

    def alert_show(msg):
        def close_dialog(e):
            page.pop_dialog()
            page.update()

        page.show_dialog(
            ft.AlertDialog(
                open=True,
                modal=True,
                title=ft.Text(msg),
                actions=[
                    ft.Button(
                        content="OK",
                        on_click=close_dialog,
                    )
                ],
            )
        )

    async def select_directory(e):
        nonlocal zip_file_name
        path = await ft.FilePicker().get_directory_path()
        if path is None:
            return
        directory_path.value = path

        zip_file_name = os.path.basename(path) + ".zip"
        page.update()

    async def select_zip_save_path(e):
        path = await ft.FilePicker().save_file(
            file_name=zip_file_name,
            allowed_extensions=["zip"],
        )
        if path is None:
            return
        # 拡張子がなかったらつける
        if not path.lower().endswith(".zip"):
            path += ".zip"

        zip_upload_path.value = path
        page.update()

    async def zip_click(e):
        if directory_path.value == "" or zip_upload_path.value == "":
            alert_show("圧縮したいフォルダと圧縮先を指定してください。")
            return
        try:
            zip_button.disabled = True
            progress.visible = True
            page.update()
            zip_name = os.path.splitext(zip_upload_path.value)[0]
            root_dir = os.path.dirname(directory_path.value)
            base_dir = os.path.basename(directory_path.value)
            # 圧縮は重い処理なので別スレッドで実行し、GUIを止めない
            await asyncio.to_thread(
                shutil.make_archive,
                zip_name,
                "zip",
                root_dir,
                base_dir,
            )
            alert_show("圧縮が完了しました。")
        except Exception as ex:
            alert_show(f"圧縮に失敗しました。({ex})")
        finally:
            # ボタンを有効化し、処理中の表示を消す
            progress.visible = False
            zip_button.disabled = False
            page.update()

    zip_button.on_click = zip_click

    page.add(
        ft.Row(
            [
                directory_path,
                ft.IconButton(
                    ft.Icons.FOLDER_OPEN,
                    on_click=select_directory,
                    disabled=page.web,
                ),
            ]
        ),
        ft.Row(
            [
                zip_button,
                progress,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        ft.Row(
            [
                zip_upload_path,
                ft.IconButton(
                    icon=ft.Icons.SAVE,
                    on_click=select_zip_save_path,
                    disabled=page.web,
                ),
            ]
        ),
    )
    page.update()


if __name__ == "__main__":
    zip_exe()
