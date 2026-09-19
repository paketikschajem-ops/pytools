from pathlib import Path
import random

import qrcode
from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

_ET_UPPER_FROM = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_ET_UPPER_TO = "QWERTYUIOPASDFGHJKLZXCVBNM"
_ET_DIGITS_FROM = "0123456789"
_ET_DIGITS_TO = "1234567890"

ET = {}
DT = {}

for source, target in zip(_ET_UPPER_FROM, _ET_UPPER_TO):
    ET[source] = target
    DT[target] = source

for source, target in zip(_ET_UPPER_FROM.lower(), _ET_UPPER_TO.lower()):
    ET[source] = target
    DT[target] = source

for source, target in zip(_ET_DIGITS_FROM, _ET_DIGITS_TO):
    ET[source] = target
    DT[target] = source

GENERATOR_CHARS = "abGhsgdgdhyHjdhfJITDCJSFCfbcj64779444444484845429898_"


class Card(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=dp(16), spacing=dp(10), **kwargs)
        with self.canvas.before:
            Color(0.12, 0.14, 0.18, 1)
            self.background = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(18)])
        self.bind(pos=self._update_background, size=self._update_background)

    def _update_background(self, *_):
        self.background.pos = self.pos
        self.background.size = self.size


class PyToolsApp(App):
    def build(self):
        self.title = "PyTools"
        Window.clearcolor = (0.06, 0.07, 0.09, 1)

        root = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(10))

        header = BoxLayout(size_hint_y=None, height=dp(58), padding=(dp(4), 0))
        title = Label(text="PyTools", font_size=dp(28), bold=True, halign="left", valign="middle")
        title.bind(size=lambda instance, value: setattr(instance, "text_size", value))
        subtitle = Label(
            text="QR • Cipher • Generator",
            font_size=dp(13),
            color=(0.65, 0.68, 0.75, 1),
            halign="right",
            valign="middle",
        )
        subtitle.bind(size=lambda instance, value: setattr(instance, "text_size", value))
        header.add_widget(title)
        header.add_widget(subtitle)
        root.add_widget(header)

        self.tabs = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(7))
        for text, callback in (
            ("QR Code", self.show_qr),
            ("Cipher", self.show_cipher),
            ("Generator", self.show_generator),
        ):
            self.tabs.add_widget(self.make_button(text, callback))
        root.add_widget(self.tabs)

        self.content = BoxLayout()
        root.add_widget(self.content)

        self.qr_screen = self.build_qr_screen()
        self.cipher_screen = self.build_cipher_screen()
        self.generator_screen = self.build_generator_screen()
        self.show_qr()
        return root

    def make_button(self, text, callback, height=46):
        button = Button(
            text=text,
            size_hint_y=None,
            height=dp(height),
            background_normal="",
            background_color=(0.16, 0.18, 0.23, 1),
            color=(0.95, 0.96, 1, 1),
            font_size=dp(15),
        )
        button.bind(on_release=callback)
        return button

    def make_input(self, hint="", multiline=False):
        return TextInput(
            hint_text=hint,
            multiline=multiline,
            size_hint_y=None,
            height=dp(52) if not multiline else dp(120),
            padding=[dp(14), dp(12)],
            font_size=dp(16),
            background_normal="",
            background_color=(0.09, 0.10, 0.13, 1),
            foreground_color=(0.95, 0.96, 1, 1),
            hint_text_color=(0.45, 0.48, 0.55, 1),
        )

    def make_label(self, text, size=15, color=(0.85, 0.87, 0.92, 1)):
        label = Label(
            text=text,
            font_size=dp(size),
            color=color,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(32),
        )
        label.bind(size=lambda instance, value: setattr(instance, "text_size", value))
        return label

    def replace_content(self, widget):
        self.content.clear_widgets()
        self.content.add_widget(widget)

    def build_qr_screen(self):
        scroll = ScrollView(do_scroll_x=False)
        box = BoxLayout(orientation="vertical", spacing=dp(12), padding=dp(4), size_hint_y=None)
        box.bind(minimum_height=box.setter("height"))

        card = Card(size_hint_y=None)
        card.add_widget(self.make_label("QR Code", 22, (1, 1, 1, 1)))
        card.add_widget(self.make_label("Enter a website or text to create a QR code.", 14))
        self.qr_input = self.make_input("example.com")
        card.add_widget(self.qr_input)

        qr_buttons = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        qr_buttons.add_widget(self.make_button("Generate QR", self.generate_qr))
        qr_buttons.add_widget(self.make_button("Save QR Image", self.save_qr))
        card.add_widget(qr_buttons)

        self.qr_status = self.make_label("Ready.", 13, (0.65, 0.68, 0.75, 1))
        card.add_widget(self.qr_status)
        self.qr_image = Image(source="", size_hint_y=None, height=dp(300), allow_stretch=True, keep_ratio=True)
        card.add_widget(self.qr_image)

        box.add_widget(card)
        scroll.add_widget(box)
        return scroll

    def normalize_qr_data(self, data):
        data = data.strip()
        if not data:
            return ""
        if not data.startswith(("http://", "https://")):
            data = "https://" + data
        return data

    def generate_qr(self, *_):
        data = self.normalize_qr_data(self.qr_input.text)
        if not data:
            self.qr_status.text = "Please enter a website or text."
            return
        try:
            qr = qrcode.make(data)
            path = Path(self.user_data_dir) / "my_qrcode.png"
            qr.save(path)
            self.qr_image.source = str(path)
            self.qr_image.reload()
            self.last_qr_path = path
            self.qr_status.text = f"QR generated for: {data}"
        except Exception as error:
            self.qr_status.text = f"QR error: {error}"

    def save_qr(self, *_):
        if not getattr(self, "last_qr_path", None):
            self.qr_status.text = "Generate a QR code first."
            return
        destination = Path(self.user_data_dir) / "PyTools_QR.png"
        try:
            destination.write_bytes(Path(self.last_qr_path).read_bytes())
            self.qr_status.text = f"Saved as {destination.name} in app storage."
        except Exception as error:
            self.qr_status.text = f"Save error: {error}"

    def build_cipher_screen(self):
        scroll = ScrollView(do_scroll_x=False)
        box = BoxLayout(orientation="vertical", spacing=dp(12), padding=dp(4), size_hint_y=None)
        box.bind(minimum_height=box.setter("height"))

        card = Card(size_hint_y=None)
        card.add_widget(self.make_label("Substitution Cipher", 22, (1, 1, 1, 1)))
        card.add_widget(self.make_label("Use the same mapping as the original console program.", 14))
        self.cipher_input = self.make_input("Text", multiline=True)
        card.add_widget(self.cipher_input)

        buttons = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        buttons.add_widget(self.make_button("Encrypt", self.encrypt_text))
        buttons.add_widget(self.make_button("Decrypt", self.decrypt_text))
        card.add_widget(buttons)

        card.add_widget(self.make_label("Result", 15))
        self.cipher_output = TextInput(
            readonly=True,
            multiline=True,
            size_hint_y=None,
            height=dp(150),
            padding=[dp(14), dp(12)],
            font_size=dp(16),
            background_normal="",
            background_color=(0.09, 0.10, 0.13, 1),
            foreground_color=(0.95, 0.96, 1, 1),
        )
        card.add_widget(self.cipher_output)
        box.add_widget(card)
        scroll.add_widget(box)
        return scroll

    def transform(self, text, mapping):
        return "".join(mapping.get(letter, letter) for letter in text)

    def encrypt_text(self, *_):
        self.cipher_output.text = self.transform(self.cipher_input.text, ET)

    def decrypt_text(self, *_):
        self.cipher_output.text = self.transform(self.cipher_input.text, DT)

    def build_generator_screen(self):
        scroll = ScrollView(do_scroll_x=False)
        box = BoxLayout(orientation="vertical", spacing=dp(12), padding=dp(4), size_hint_y=None)
        box.bind(minimum_height=box.setter("height"))

        card = Card(size_hint_y=None)
        card.add_widget(self.make_label("Code Generator", 22, (1, 1, 1, 1)))
        card.add_widget(self.make_label("Generate a random code using the original character set.", 14))

        buttons = GridLayout(cols=3, spacing=dp(8), size_hint_y=None, height=dp(48))
        buttons.add_widget(self.make_button("6", lambda *_: self.generate_code(6)))
        buttons.add_widget(self.make_button("8", lambda *_: self.generate_code(8)))
        buttons.add_widget(self.make_button("12", lambda *_: self.generate_code(12)))
        card.add_widget(buttons)

        self.generator_output = TextInput(
            readonly=True,
            multiline=False,
            size_hint_y=None,
            height=dp(58),
            padding=[dp(14), dp(14)],
            font_size=dp(20),
            background_normal="",
            background_color=(0.09, 0.10, 0.13, 1),
            foreground_color=(0.95, 0.96, 1, 1),
            halign="center",
        )
        card.add_widget(self.generator_output)
        self.generator_status = self.make_label("Choose a length.", 13, (0.65, 0.68, 0.75, 1))
        card.add_widget(self.generator_status)

        box.add_widget(card)
        scroll.add_widget(box)
        return scroll

    def generate_code(self, length):
        result = "".join(random.choice(GENERATOR_CHARS) for _ in range(length))
        self.generator_output.text = result
        self.generator_status.text = f"Generated {length}-character code."

    def show_qr(self, *_):
        self.replace_content(self.qr_screen)

    def show_cipher(self, *_):
        self.replace_content(self.cipher_screen)

    def show_generator(self, *_):
        self.replace_content(self.generator_screen)


if __name__ == "__main__":
    PyToolsApp().run()
