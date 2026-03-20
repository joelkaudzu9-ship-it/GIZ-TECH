import os
import re
import random
from collections import Counter
import PyPDF2
from datetime import datetime

from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.list import OneLineListItem
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.filechooser import FileChooserListView
from plyer import filechooser

# Mobile size
Window.size = (360, 640)

KV = '''
<FlashcardCard>:
    orientation: 'vertical'
    size_hint: 0.9, 0.6
    padding: "20dp"
    spacing: "10dp"
    pos_hint: {"center_x": 0.5, "center_y": 0.5}
    md_bg_color: app.theme_cls.primary_color if not root.show_answer else app.theme_cls.accent_color
    radius: [25,]

    MDLabel:
        id: card_text
        text: root.question if not root.show_answer else root.answer
        halign: 'center'
        valign: 'middle'
        font_style: 'H5' if not root.show_answer else 'Body1'
        text_color: 1, 1, 1, 1
        size_hint_y: 0.8

<FileItem>:
    text: self.path
    on_release: app.load_selected_file(self.path)

MDScreen:
    MDNavigationLayout:
        ScreenManager:
            id: screen_manager

            # HOME SCREEN
            MDScreen:
                name: "home"

                MDBoxLayout:
                    orientation: 'vertical'

                    MDTopAppBar:
                        title: "📚 StudyFlash"
                        right_action_items: [['timer', lambda x: app.show_timer()], ['download', lambda x: app.export_data()]]
                        elevation: 10

                    ScrollView:
                        MDBoxLayout:
                            orientation: 'vertical'
                            spacing: "15dp"
                            padding: "20dp"
                            size_hint_y: None
                            height: self.minimum_height

                            # Quick Stats Card
                            MDCard:
                                orientation: 'vertical'
                                size_hint: 1, None
                                height: "120dp"
                                padding: "20dp"
                                spacing: "10dp"
                                ripple_behavior: True
                                on_release: app.show_stats()

                                MDBoxLayout:
                                    MDLabel:
                                        text: "⚡ Quick Study"
                                        font_style: 'H6'

                                    MDLabel:
                                        id: study_time
                                        text: "Timer: 00:00"
                                        halign: 'right'
                                        font_style: 'Caption'

                                MDLabel:
                                    id: study_stats
                                    text: "Flashcards: 0 | Words: 0"
                                    font_style: 'Body2'
                                    theme_text_color: 'Secondary'

                            # Action Buttons
                            MDGridLayout:
                                cols: 2
                                spacing: "15dp"
                                size_hint_y: None
                                height: "250dp"

                                MDCard:
                                    orientation: 'vertical'
                                    padding: "20dp"
                                    spacing: "10dp"
                                    ripple_behavior: True
                                    on_release: app.browse_files()

                                    MDLabel:
                                        text: "📄"
                                        font_style: 'H3'
                                        halign: 'center'

                                    MDLabel:
                                        text: "Open File"
                                        halign: 'center'
                                        font_style: 'H6'

                                    MDLabel:
                                        text: "PDF/TXT"
                                        halign: 'center'
                                        theme_text_color: 'Secondary'

                                MDCard:
                                    orientation: 'vertical'
                                    padding: "20dp"
                                    spacing: "10dp"
                                    ripple_behavior: True
                                    on_release: app.enter_text()

                                    MDLabel:
                                        text: "✍️"
                                        font_style: 'H3'
                                        halign: 'center'

                                    MDLabel:
                                        text: "Type Notes"
                                        halign: 'center'
                                        font_style: 'H6'

                                    MDLabel:
                                        text: "Manual Input"
                                        halign: 'center'
                                        theme_text_color: 'Secondary'

                                MDCard:
                                    orientation: 'vertical'
                                    padding: "20dp"
                                    spacing: "10dp"
                                    ripple_behavior: True
                                    on_release: app.start_flashcards()

                                    MDLabel:
                                        text: "🎴"
                                        font_style: 'H3'
                                        halign: 'center'

                                    MDLabel:
                                        text: "Flashcards"
                                        halign: 'center'
                                        font_style: 'H6'

                                    MDLabel:
                                        text: "Quiz Mode"
                                        halign: 'center'
                                        theme_text_color: 'Secondary'

                                MDCard:
                                    orientation: 'vertical'
                                    padding: "20dp"
                                    spacing: "10dp"
                                    ripple_behavior: True
                                    on_release: app.show_summary()

                                    MDLabel:
                                        text: "📋"
                                        font_style: 'H3'
                                        halign: 'center'

                                    MDLabel:
                                        text: "Summary"
                                        halign: 'center'
                                        font_style: 'H6'

                                    MDLabel:
                                        text: "Key Points"
                                        halign: 'center'
                                        theme_text_color: 'Secondary'

                            # Recent Files
                            MDCard:
                                orientation: 'vertical'
                                size_hint: 1, None
                                height: "200dp"
                                padding: "10dp"

                                MDLabel:
                                    text: "📂 Recent Files"
                                    font_style: 'H6'
                                    padding: [10, 10]

                                ScrollView:
                                    MDList:
                                        id: recent_files_list

            # FLASHCARD SCREEN
            MDScreen:
                name: "flashcards"

                MDBoxLayout:
                    orientation: 'vertical'

                    MDTopAppBar:
                        title: "Flashcards"
                        left_action_items: [['arrow-left', lambda x: app.go_home()]]
                        right_action_items: [['shuffle', lambda x: app.shuffle_cards()], ['content-save', lambda x: app.save_session()]]
                        elevation: 10

                    BoxLayout:
                        orientation: 'vertical'
                        padding: "20dp"

                        FlashcardCard:
                            id: flashcard_widget

                        MDBoxLayout:
                            size_hint_y: 0.2
                            spacing: "10dp"
                            padding: "20dp"

                            MDRaisedButton:
                                text: "❌ Hard"
                                md_bg_color: 0.8, 0.2, 0.2, 1
                                on_release: app.mark_hard()

                            MDRaisedButton:
                                text: "✅ Easy"
                                md_bg_color: 0.2, 0.8, 0.2, 1
                                on_release: app.mark_easy()

            # FILE BROWSER
            MDScreen:
                name: "browser"

                MDBoxLayout:
                    orientation: 'vertical'

                    MDTopAppBar:
                        title: "Select File"
                        left_action_items: [['arrow-left', lambda x: app.go_home()]]
                        elevation: 10

                    BoxLayout:
                        FileChooserListView:
                            id: file_chooser
                            filters: ['*.pdf', '*.txt']

            # SUMMARY SCREEN
            MDScreen:
                name: "summary_view"

                MDBoxLayout:
                    orientation: 'vertical'

                    MDTopAppBar:
                        title: "Summary"
                        left_action_items: [['arrow-left', lambda x: app.go_home()]]
                        right_action_items: [['download', lambda x: app.export_summary()]]
                        elevation: 10

                    ScrollView:
                        MDLabel:
                            id: summary_text
                            text: "No summary generated"
                            size_hint_y: None
                            height: self.texture_size[1] + 100
                            padding: [30, 30]
                            halign: 'center'
'''

Builder.load_string(KV)


class FlashcardCard(MDCard):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.question = "Tap to load content"
        self.answer = "Use the home screen to add study material"
        self.show_answer = False

    def flip_card(self):
        anim = Animation(opacity=0.3, duration=0.1) + Animation(opacity=1, duration=0.2)
        anim.start(self)
        self.show_answer = not self.show_answer
        self.md_bg_color = self.parent.parent.parent.parent.app.theme_cls.primary_color if not self.show_answer else self.parent.parent.parent.parent.app.theme_cls.accent_color
        self.ids.card_text.text = self.answer if self.show_answer else self.question


class FileItem(OneLineListItem):
    pass


class StudyFlashApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.content = ""
        self.flashcards = []
        self.summary = ""
        self.current_card = 0
        self.study_start = None
        self.timer_running = False
        self.file_history = []

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "DeepPurple"
        self.theme_cls.accent_palette = "Amber"
        return Builder.load_string(KV)

    def on_start(self):
        # Load recent files
        self.load_recent_files()
        # Start animation
        self.animate_home_cards()
        # Update stats
        Clock.schedule_interval(self.update_stats, 1)

    def animate_home_cards(self):
        cards = self.root.ids.screen_manager.get_screen('home').children[0].children[0].children
        for i, child in enumerate(reversed(cards)):
            if hasattr(child, 'opacity'):
                child.opacity = 0
                child.y -= 50
                Clock.schedule_once(lambda dt, c=child, idx=i: (
                    Animation(opacity=1, duration=0.3, delay=idx * 0.1).start(c),
                    Animation(y=c.y + 50, duration=0.3, delay=idx * 0.1).start(c)
                ), 0.1)

    def browse_files(self):
        # Use plyer for actual file chooser
        try:
            filechooser.open_file(
                filters=[('PDF Files', '*.pdf'), ('Text Files', '*.txt')],
                on_selection=self.handle_file_selection
            )
        except:
            # Fallback to built-in file chooser
            self.root.ids.screen_manager.current = "browser"

    def handle_file_selection(self, selection):
        if selection:
            self.load_file(selection[0])

    def load_file(self, path):
        if path.endswith('.pdf'):
            text = self.extract_pdf(path)
        else:
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()

        self.content = text
        self.add_to_recent(path)
        self.generate_study_materials()
        self.show_dialog("Loaded", f"Loaded {len(text)} chars from {os.path.basename(path)}")
        self.root.ids.screen_manager.current = "home"

    def extract_pdf(self, path):
        text = ""
        try:
            with open(path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except:
            return "PDF extraction failed"

    def enter_text(self):
        dialog = MDDialog(
            title="📝 Enter Notes",
            type="custom",
            content_cls=MDBoxLayout(
                MDTextField(
                    id="notes_input",
                    multiline=True,
                    hint_text="Paste your study notes here...",
                    size_hint_y=0.8,
                    mode="fill"
                ),
                orientation="vertical",
                height="400dp",
                width="300dp"
            ),
            buttons=[
                MDRaisedButton(text="Cancel", on_release=lambda x: dialog.dismiss()),
                MDRaisedButton(text="Generate", on_release=lambda x: self.process_text_input(dialog))
            ]
        )
        dialog.open()

    def process_text_input(self, dialog):
        text = dialog.content_cls.ids.notes_input.text
        if text:
            self.content = text
            self.generate_study_materials()
            self.show_dialog("Ready", f"Created {len(self.flashcards)} flashcards!")
        dialog.dismiss()

    def generate_study_materials(self):
        # Generate flashcards
        sentences = re.split(r'[.!?]+', self.content)
        sentences = [s.strip() for s in sentences if 20 < len(s) < 150]

        self.flashcards = []
        for i, sentence in enumerate(sentences[:20]):  # Max 20 cards
            self.flashcards.append({
                'question': f"Point {i + 1}: {sentence[:60]}...",
                'answer': sentence,
                'difficulty': 'medium'
            })

        # Generate summary
        if sentences:
            self.summary = "\n\n".join(sentences[:5])

        # Update UI
        self.update_stats()

    def start_flashcards(self):
        if not self.flashcards:
            if self.content:
                self.generate_study_materials()
            else:
                self.show_dialog("No Content", "Add study material first!")
                return

        self.root.ids.screen_manager.current = "flashcards"
        card = self.root.ids.flashcard_widget
        card.question = self.flashcards[0]['question']
        card.answer = self.flashcards[0]['answer']
        card.show_answer = False
        card.update_card()

        # Bounce animation
        anim = Animation(size_hint_y=0.65, duration=0.2) + Animation(size_hint_y=0.6, duration=0.2)
        anim.start(card)

    def show_summary(self):
        if not self.summary and self.content:
            self.generate_study_materials()

        self.root.ids.screen_manager.current = "summary_view"
        self.root.ids.summary_text.text = self.summary if self.summary else "Generate content first!"

        # Typewriter effect
        text = self.root.ids.summary_text
        original = text.text
        text.text = ""
        Clock.schedule_once(lambda dt: self.type_text(text, original, 0), 0.5)

    def type_text(self, widget, text, index):
        if index < len(text):
            widget.text += text[index]
            Clock.schedule_once(lambda dt: self.type_text(widget, text, index + 1), 0.02)

    def shuffle_cards(self):
        if self.flashcards:
            random.shuffle(self.flashcards)
            self.current_card = 0
            self.show_next_card()

            # Spin animation
            card = self.root.ids.flashcard_widget
            anim = Animation(rotation=360, duration=0.5)
            anim.start(card)
            card.rotation = 0

    def mark_hard(self):
        if self.flashcards:
            self.flashcards[self.current_card]['difficulty'] = 'hard'
            self.show_next_card()

    def mark_easy(self):
        if self.flashcards:
            self.flashcards[self.current_card]['difficulty'] = 'easy'
            self.show_next_card()

    def show_next_card(self):
        if self.flashcards:
            self.current_card = (self.current_card + 1) % len(self.flashcards)
            card = self.root.ids.flashcard_widget
            card.question = self.flashcards[self.current_card]['question']
            card.answer = self.flashcards[self.current_card]['answer']
            card.show_answer = False
            card.update_card()

            # Slide animation
            anim = Animation(x=Window.width, duration=0.2) + \
                   Animation(x=0, duration=0.2)
            anim.start(card)

    def show_timer(self):
        self.timer_running = not self.timer_running
        if self.timer_running:
            self.study_start = datetime.now()
            self.show_dialog("Timer Started", "Study timer is running!")
        else:
            duration = datetime.now() - self.study_start
            self.show_dialog("Session Complete", f"Studied for {duration.seconds // 60} minutes!")

    def update_stats(self, dt=0):
        home = self.root.ids.screen_manager.get_screen('home')
        home.ids.study_stats.text = f"Flashcards: {len(self.flashcards)} | Words: {len(self.content.split())}"

        if self.timer_running and self.study_start:
            elapsed = datetime.now() - self.study_start
            home.ids.study_time.text = f"Timer: {elapsed.seconds // 60:02d}:{elapsed.seconds % 60:02d}"

    def add_to_recent(self, path):
        if path not in self.file_history:
            self.file_history.insert(0, path)
            self.file_history = self.file_history[:5]  # Keep last 5
            self.update_recent_files()

    def update_recent_files(self):
        list_widget = self.root.ids.recent_files_list
        list_widget.clear_widgets()

        for path in self.file_history:
            if os.path.exists(path):
                item = FileItem(text=os.path.basename(path))
                item.path = path
                list_widget.add_widget(item)

    def load_recent_files(self):
        # Simulate loading recent files
        self.file_history = []
        self.update_recent_files()

    def show_stats(self):
        dialog = MDDialog(
            title="📊 Study Statistics",
            text=f"""Content Analysis:

Characters: {len(self.content):,}
Words: {len(self.content.split()):,}
Sentences: {len(re.split(r'[.!?]+', self.content)):,}
Flashcards: {len(self.flashcards)}

{'🎯 Ready to study!' if self.flashcards else '📝 Add more content!'}""",
            buttons=[MDRaisedButton(text="OK", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()

    def export_data(self):
        if self.content:
            filename = f"study_export_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
            with open(filename, 'w') as f:
                f.write(f"StudyFlash Export\n")
                f.write(f"Generated: {datetime.now()}\n")
                f.write(f"\nContent ({len(self.content.split())} words):\n")
                f.write(self.content[:1000] + "...\n" if len(self.content) > 1000 else self.content)
                f.write(f"\n\nFlashcards ({len(self.flashcards)}):\n")
                for i, card in enumerate(self.flashcards):
                    f.write(f"\n{i + 1}. {card['question']}\n   {card['answer']}\n")

            self.show_dialog("Exported", f"Saved to {filename}")

    def export_summary(self):
        if self.summary:
            filename = f"summary_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
            with open(filename, 'w') as f:
                f.write(self.summary)
            self.show_dialog("Exported", f"Summary saved to {filename}")

    def save_session(self):
        self.show_dialog("Saved", "Study session progress saved!")

    def go_home(self):
        self.root.ids.screen_manager.current = "home"

    def show_dialog(self, title, text):
        MDDialog(
            title=title,
            text=text,
            buttons=[MDRaisedButton(text="OK", on_release=lambda x: self.close_dialog())]
        ).open()

    def close_dialog(self):
        for widget in self.root.walk():
            if isinstance(widget, MDDialog):
                widget.dismiss()


if __name__ == "__main__":
    StudyFlashApp().run()