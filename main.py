from datetime import date, timedelta
import json
import os
import re

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup

# Keep the text boxes visible when the Android keyboard opens
Window.softinput_mode = "below_target"


def add_days(start, days):
    return start + timedelta(days=days)


def parse_date(text):
    """Parse DD-MM-YYYY. Also accepts / or . separators and single-digit day/month."""
    parts = re.split(r"[-/.\s]+", text.strip())
    if len(parts) != 3:
        raise ValueError("bad format")
    day, month, year = (int(p) for p in parts)
    if year < 1900:
        raise ValueError("bad year")
    return date(year, month, day)


def wrap_label(label):
    """Make a Label wrap its text to its own width."""
    label.bind(width=lambda inst, w: setattr(inst, "text_size", (w, None)))
    return label


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="vertical", padding=20, spacing=15)

        root.add_widget(Label(
            text="TB PATIENT FOLLOW-UP",
            font_size=26,
            bold=True,
            size_hint_y=None,
            height=60
        ))
        root.add_widget(Label(
            text="Calculate and save follow-up dates",
            font_size=17,
            size_hint_y=None,
            height=40
        ))

        new_btn = Button(text="NEW PATIENT", font_size=19, size_hint_y=None, height=60)
        new_btn.bind(on_press=lambda *_: setattr(self.manager, "current", "new"))
        root.add_widget(new_btn)

        saved_btn = Button(text="SAVED PATIENTS", font_size=19, size_hint_y=None, height=60)
        saved_btn.bind(on_press=lambda *_: setattr(self.manager, "current", "patients"))
        root.add_widget(saved_btn)

        root.add_widget(Label(
            text="Follow-up schedule:\nMonth 2 = +56 days\nMonth 5 = +140 days\nMonth 6 = +168 days",
            font_size=17,
            halign="center"
        ))
        self.add_widget(root)


class NewPatientScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="vertical", padding=20, spacing=12)

        root.add_widget(Label(text="NEW TB PATIENT", font_size=24, bold=True,
                              size_hint_y=None, height=55))

        self.name_input = TextInput(hint_text="Patient name", multiline=False,
                                    font_size=18, size_hint_y=None, height=55)
        self.id_input = TextInput(hint_text="Patient ID", multiline=False,
                                  font_size=18, size_hint_y=None, height=55)
        self.date_input = TextInput(
            hint_text="Treatment start date: DD-MM-YYYY",
            multiline=False, font_size=18, size_hint_y=None, height=55
        )

        root.add_widget(self.name_input)
        root.add_widget(self.id_input)
        root.add_widget(self.date_input)

        calc = Button(text="CALCULATE & SAVE", font_size=18,
                      size_hint_y=None, height=60)
        calc.bind(on_press=self.calculate_save)
        root.add_widget(calc)

        back = Button(text="BACK", size_hint_y=None, height=50)
        back.bind(on_press=lambda *_: setattr(self.manager, "current", "home"))
        root.add_widget(back)

        self.result = wrap_label(Label(text="", font_size=17, halign="left", valign="top"))
        root.add_widget(self.result)

        self.add_widget(root)

    def on_leave(self, *args):
        self.result.text = ""

    def calculate_save(self, *_):
        name = self.name_input.text.strip()
        patient_id = self.id_input.text.strip()
        date_text = self.date_input.text.strip()

        if not name or not patient_id or not date_text:
            self.result.text = "Please enter patient name, ID and start date."
            return

        try:
            start = parse_date(date_text)
        except Exception:
            self.result.text = "Invalid date. Use DD-MM-YYYY (e.g. 05-03-2026)."
            return

        app = App.get_running_app()

        if any(r["patient_id"].lower() == patient_id.lower() for r in app.records):
            self.result.text = f"Patient ID '{patient_id}' is already saved.\nUse a different ID."
            return

        record = {
            "name": name,
            "patient_id": patient_id,
            "start_date": start.strftime("%d-%m-%Y"),
            "month_2": add_days(start, 56).strftime("%d-%m-%Y"),
            "month_5": add_days(start, 140).strftime("%d-%m-%Y"),
            "month_6": add_days(start, 168).strftime("%d-%m-%Y"),
        }

        app.records.append(record)
        if not app.save_records():
            app.records.pop()
            self.result.text = "Could not save the record. Check phone storage."
            return

        self.result.text = (
            f"Saved successfully!\n\n"
            f"Patient: {name}\n"
            f"ID: {patient_id}\n\n"
            f"Start: {record['start_date']}\n"
            f"Month 2: {record['month_2']}\n"
            f"Month 5: {record['month_5']}\n"
            f"Month 6: {record['month_6']}"
        )

        self.name_input.text = ""
        self.id_input.text = ""
        self.date_input.text = ""


class PatientsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="vertical", padding=15, spacing=10)
        root.add_widget(Label(text="SAVED PATIENTS", font_size=24, bold=True,
                              size_hint_y=None, height=55))
        root.add_widget(Label(text="Tap a patient to delete", font_size=14,
                              size_hint_y=None, height=25))

        self.scroll = ScrollView()
        self.list_box = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.list_box.bind(minimum_height=self.list_box.setter("height"))
        self.scroll.add_widget(self.list_box)
        root.add_widget(self.scroll)

        back = Button(text="BACK", size_hint_y=None, height=50)
        back.bind(on_press=lambda *_: setattr(self.manager, "current", "home"))
        root.add_widget(back)
        self.add_widget(root)

    def on_pre_enter(self, *args):
        self.refresh()

    def refresh(self):
        self.list_box.clear_widgets()
        records = App.get_running_app().records

        if not records:
            self.list_box.add_widget(Label(
                text="No saved patients.",
                size_hint_y=None, height=50
            ))
            return

        for i, r in enumerate(records):
            text = (
                f"{r['name']} | ID: {r['patient_id']}\n"
                f"Start: {r['start_date']}\n"
                f"Month 2: {r['month_2']}   Month 5: {r['month_5']}   Month 6: {r['month_6']}"
            )
            btn = Button(text=text, halign="left", valign="middle",
                         size_hint_y=None, height=120)
            btn.bind(width=lambda inst, w: setattr(inst, "text_size", (w - 20, None)))
            btn.bind(on_press=lambda _, index=i: self.confirm_delete(index))
            self.list_box.add_widget(btn)

    def confirm_delete(self, index):
        def delete(*_):
            app = App.get_running_app()
            if 0 <= index < len(app.records):
                del app.records[index]
                app.save_records()
            popup.dismiss()
            self.refresh()

        r = App.get_running_app().records[index]
        box = BoxLayout(orientation="vertical", padding=15, spacing=10)
        box.add_widget(Label(text=f"Delete record for\n{r['name']} (ID: {r['patient_id']})?",
                             halign="center"))
        yes = Button(text="DELETE", size_hint_y=None, height=50)
        no = Button(text="CANCEL", size_hint_y=None, height=50)
        box.add_widget(yes)
        box.add_widget(no)
        popup = Popup(title="Confirm deletion", content=box,
                      size_hint=(0.85, 0.45))
        yes.bind(on_press=delete)
        no.bind(on_press=popup.dismiss)
        popup.open()


class TBFollowupApp(App):
    def build(self):
        self.title = "TB Follow-up Calculator"
        self.records = []
        self.load_records()

        self.sm = ScreenManager()
        self.sm.add_widget(HomeScreen(name="home"))
        self.sm.add_widget(NewPatientScreen(name="new"))
        self.sm.add_widget(PatientsScreen(name="patients"))

        # Android back button (mapped to Esc key 27)
        Window.bind(on_keyboard=self.on_back_key)
        return self.sm

    def on_back_key(self, window, key, *args):
        if key == 27 and self.sm.current != "home":
            self.sm.current = "home"
            return True
        return False

    def data_file(self):
        return os.path.join(self.user_data_dir, "patients.json")

    def load_records(self):
        try:
            with open(self.data_file(), "r", encoding="utf-8") as f:
                data = json.load(f)
            self.records = data if isinstance(data, list) else []
        except Exception:
            self.records = []

    def save_records(self):
        try:
            os.makedirs(self.user_data_dir, exist_ok=True)
            tmp = self.data_file() + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self.records, f, indent=2)
            os.replace(tmp, self.data_file())  # atomic: no half-written file
            return True
        except Exception:
            return False


if __name__ == "__main__":
    TBFollowupApp().run()
