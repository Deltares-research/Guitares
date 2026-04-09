"""Tests for all guitares widget types (PySide6 framework)."""

import pandas as pd


class TestEditBox:
    """Tests for style: edit."""

    CONFIG = """\
window:
  title: Test Edit
  width: 300
  height: 80
  variable_group: grp
element:
- style: edit
  position: {x: 100, y: 10, width: 150, height: 24}
  variable: name
  text: Name
"""

    def test_creates_widget(self, make_gui):
        gui = make_gui(self.CONFIG, {"grp": {"name": "hello"}})
        assert gui.getvar("grp", "name") == "hello"

    def test_set_and_get(self, make_gui):
        gui = make_gui(self.CONFIG, {"grp": {"name": ""}})
        gui.setvar("grp", "name", "world")
        assert gui.getvar("grp", "name") == "world"

    def test_numeric_variable(self, make_gui):
        gui = make_gui(self.CONFIG, {"grp": {"name": 42}})
        assert gui.getvar("grp", "name") == 42

    def test_float_variable(self, make_gui):
        gui = make_gui(self.CONFIG, {"grp": {"name": 3.14}})
        assert gui.getvar("grp", "name") == 3.14


class TestSpinBox:
    """Tests for style: spinbox."""

    CONFIG = """\
window:
  title: Test Spinbox
  width: 300
  height: 80
  variable_group: grp
element:
- style: spinbox
  position: {x: 100, y: 10, width: 120, height: 24}
  variable: value
  minimum: 0
  maximum: 100
  step: 5
  text: Value
"""

    def test_creates_widget(self, make_gui):
        gui = make_gui(self.CONFIG, {"grp": {"value": 50}})
        assert gui.getvar("grp", "value") == 50

    def test_float_spinbox(self, make_gui):
        gui = make_gui(self.CONFIG, {"grp": {"value": 2.5}})
        assert gui.getvar("grp", "value") == 2.5


class TestText:
    """Tests for style: text."""

    CONFIG = """\
window:
  title: Test Text
  width: 300
  height: 80
  variable_group: grp
element:
- style: text
  position: {x: 10, y: 10, width: 200, height: 20}
  variable: message
"""

    def test_creates_widget(self, make_gui):
        gui = make_gui(self.CONFIG, {"grp": {"message": "Hello!"}})
        assert gui.getvar("grp", "message") == "Hello!"

    def test_update_text(self, make_gui):
        gui = make_gui(self.CONFIG, {"grp": {"message": ""}})
        gui.setvar("grp", "message", "Updated")
        assert gui.getvar("grp", "message") == "Updated"


class TestPushButton:
    """Tests for style: pushbutton."""

    CONFIG = """\
window:
  title: Test Button
  width: 300
  height: 80
  variable_group: grp
element:
- style: pushbutton
  position: {x: 10, y: 10, width: 120, height: 28}
  text: Click Me
"""

    def test_creates_widget(self, make_gui):
        gui = make_gui(self.CONFIG)
        # Button doesn't need variables, just verify it builds
        assert gui.window is not None


class TestPopupMenu:
    """Tests for style: popupmenu."""

    CONFIG_STATIC = """\
window:
  title: Test Popup
  width: 300
  height: 80
  variable_group: grp
element:
- style: popupmenu
  position: {x: 100, y: 10, width: 120, height: 24}
  variable: choice
  select: item
  option_string: [A, B, C]
  option_value: [a, b, c]
"""

    CONFIG_DYNAMIC = """\
window:
  title: Test Popup Dynamic
  width: 300
  height: 80
  variable_group: grp
element:
- style: popupmenu
  position: {x: 100, y: 10, width: 120, height: 24}
  variable: choice
  select: item
  option_string: {variable: options_text}
  option_value: {variable: options_val}
"""

    CONFIG_INDEX = """\
window:
  title: Test Popup Index
  width: 300
  height: 80
  variable_group: grp
element:
- style: popupmenu
  position: {x: 100, y: 10, width: 120, height: 24}
  variable: idx
  select: index
  option_string: [X, Y, Z]
"""

    def test_static_list(self, make_gui):
        gui = make_gui(self.CONFIG_STATIC, {"grp": {"choice": "a"}})
        assert gui.getvar("grp", "choice") == "a"

    def test_dynamic_list(self, make_gui):
        gui = make_gui(
            self.CONFIG_DYNAMIC,
            {
                "grp": {
                    "choice": "b",
                    "options_text": ["A", "B", "C"],
                    "options_val": ["a", "b", "c"],
                }
            },
        )
        assert gui.getvar("grp", "choice") == "b"

    def test_index_select(self, make_gui):
        gui = make_gui(self.CONFIG_INDEX, {"grp": {"idx": 0}})
        assert gui.getvar("grp", "idx") == 0


class TestListBox:
    """Tests for style: listbox."""

    CONFIG_SINGLE = """\
window:
  title: Test Listbox
  width: 300
  height: 120
  variable_group: grp
element:
- style: listbox
  position: {x: 10, y: 10, width: 200, height: 80}
  variable: selected
  select: item
  option_string: {variable: items_text}
  option_value: {variable: items_val}
"""

    CONFIG_MULTI = """\
window:
  title: Test Listbox Multi
  width: 300
  height: 120
  variable_group: grp
element:
- style: listbox
  position: {x: 10, y: 10, width: 200, height: 80}
  variable: selected
  select: item
  multiselection: true
  option_string: {variable: items_text}
  option_value: {variable: items_val}
"""

    def test_single_selection(self, make_gui):
        gui = make_gui(
            self.CONFIG_SINGLE,
            {
                "grp": {
                    "selected": "a",
                    "items_text": ["A", "B", "C"],
                    "items_val": ["a", "b", "c"],
                }
            },
        )
        assert gui.getvar("grp", "selected") == "a"

    def test_multi_selection(self, make_gui):
        gui = make_gui(
            self.CONFIG_MULTI,
            {
                "grp": {
                    "selected": ["a", "b"],
                    "items_text": ["A", "B", "C"],
                    "items_val": ["a", "b", "c"],
                }
            },
        )
        assert gui.getvar("grp", "selected") == ["a", "b"]


class TestCheckBox:
    """Tests for style: checkbox."""

    CONFIG = """\
window:
  title: Test Checkbox
  width: 300
  height: 80
  variable_group: grp
element:
- style: checkbox
  position: {x: 10, y: 10, width: 150, height: 20}
  variable: checked
  text: Enable feature
"""

    def test_checked(self, make_gui):
        gui = make_gui(self.CONFIG, {"grp": {"checked": True}})
        assert gui.getvar("grp", "checked") is True

    def test_unchecked(self, make_gui):
        gui = make_gui(self.CONFIG, {"grp": {"checked": False}})
        assert gui.getvar("grp", "checked") is False


class TestRadioButtonGroup:
    """Tests for style: radiobuttongroup."""

    CONFIG = """\
window:
  title: Test Radio
  width: 300
  height: 100
  variable_group: grp
element:
- style: radiobuttongroup
  position: {x: 10, y: 10, width: 200, height: 60}
  variable: method
  option_string: [Nearest, Linear, Cubic]
  option_value: [nearest, linear, cubic]
"""

    def test_creates_widget(self, make_gui):
        gui = make_gui(self.CONFIG, {"grp": {"method": "linear"}})
        assert gui.getvar("grp", "method") == "linear"

    def test_first_option(self, make_gui):
        gui = make_gui(self.CONFIG, {"grp": {"method": "nearest"}})
        assert gui.getvar("grp", "method") == "nearest"


class TestSlider:
    """Tests for style: slider."""

    CONFIG = """\
window:
  title: Test Slider
  width: 400
  height: 80
  variable_group: grp
element:
- style: slider
  position: {x: 10, y: 10, width: 300, height: 24}
  variable: year
  minimum: 2000
  maximum: 2100
"""

    def test_creates_widget(self, make_gui):
        gui = make_gui(self.CONFIG, {"grp": {"year": 2050}})
        assert gui.getvar("grp", "year") == 2050

    def test_min_value(self, make_gui):
        gui = make_gui(self.CONFIG, {"grp": {"year": 2000}})
        assert gui.getvar("grp", "year") == 2000

    def test_max_value(self, make_gui):
        gui = make_gui(self.CONFIG, {"grp": {"year": 2100}})
        assert gui.getvar("grp", "year") == 2100


class TestDateTimeEdit:
    """Tests for style: datetimeedit."""

    CONFIG = """\
window:
  title: Test DateTime
  width: 300
  height: 80
  variable_group: grp
element:
- style: datetimeedit
  position: {x: 100, y: 10, width: 150, height: 24}
  variable: dt
  text: Date
"""

    def test_creates_widget(self, make_gui):
        from datetime import datetime

        gui = make_gui(self.CONFIG, {"grp": {"dt": datetime(2024, 1, 15, 12, 0)}})
        assert gui.getvar("grp", "dt") == datetime(2024, 1, 15, 12, 0)


class TestTableView:
    """Tests for style: tableview (read-only)."""

    CONFIG = """\
window:
  title: Test TableView
  width: 300
  height: 200
  variable_group: grp
element:
- style: tableview
  position: {x: 10, y: 10, width: -10, height: 150}
  variable: selected
  option_value: {variable: df}
  selection_type: single
"""

    def test_creates_widget(self, make_gui):
        df = pd.DataFrame({"name": ["a", "b", "c"], "value": [1, 2, 3]})
        gui = make_gui(self.CONFIG, {"grp": {"df": df, "selected": [0]}})
        assert gui.getvar("grp", "selected") == [0]

    def test_empty_dataframe(self, make_gui):
        df = pd.DataFrame({"name": [], "value": []})
        gui = make_gui(self.CONFIG, {"grp": {"df": df, "selected": []}})
        assert gui.getvar("grp", "selected") == []


class TestTable:
    """Tests for style: table (editable)."""

    CONFIG = """\
window:
  title: Test Table
  width: 300
  height: 200
  variable_group: grp
element:
- style: table
  position: {x: 10, y: 10, width: -10, height: 150}
  text: Data
  option_value: {variable: df}
"""

    def test_creates_widget(self, make_gui):
        df = pd.DataFrame({"name": ["a", "b"], "value": [1.0, 2.0]})
        gui = make_gui(self.CONFIG, {"grp": {"df": df}})
        result = gui.getvar("grp", "df")
        assert len(result) == 2

    def test_empty_dataframe(self, make_gui):
        df = pd.DataFrame()
        gui = make_gui(self.CONFIG, {"grp": {"df": df}})
        result = gui.getvar("grp", "df")
        assert len(result) == 0


class TestPanel:
    """Tests for style: panel with nested elements."""

    CONFIG = """\
window:
  title: Test Panel
  width: 400
  height: 200
  variable_group: grp
element:
- style: panel
  id: settings
  title: Settings
  position: {x: 10, y: 10, width: 380, height: 180}
  element:
  - style: edit
    position: {x: 10, y: 10, width: 100, height: 24}
    variable: name
  - style: checkbox
    position: {x: 10, y: 40, width: 150, height: 20}
    variable: flag
    text: Enable
"""

    def test_nested_elements(self, make_gui):
        gui = make_gui(self.CONFIG, {"grp": {"name": "test", "flag": True}})
        assert gui.getvar("grp", "name") == "test"
        assert gui.getvar("grp", "flag") is True


class TestTabPanel:
    """Tests for style: tabpanel."""

    CONFIG = """\
window:
  title: Test Tabs
  width: 400
  height: 200
  variable_group: grp
element:
- style: tabpanel
  position: {x: 0, y: 0, width: 400, height: 200}
  tab:
  - text: Tab 1
    element:
    - style: text
      position: {x: 10, y: 10, width: 200, height: 20}
      variable: msg1
  - text: Tab 2
    element:
    - style: text
      position: {x: 10, y: 10, width: 200, height: 20}
      variable: msg2
"""

    def test_creates_tabs(self, make_gui):
        gui = make_gui(self.CONFIG, {"grp": {"msg1": "Tab 1", "msg2": "Tab 2"}})
        assert gui.getvar("grp", "msg1") == "Tab 1"
        assert gui.getvar("grp", "msg2") == "Tab 2"


class TestMultipleWidgets:
    """Test a form with multiple widget types together."""

    CONFIG = """\
window:
  title: Mixed Form
  width: 500
  height: 300
  variable_group: form
element:
- style: edit
  position: {x: 100, y: 10, width: 150, height: 24}
  variable: name
  text: Name
- style: popupmenu
  position: {x: 100, y: 40, width: 150, height: 24}
  variable: color
  select: item
  option_string: [Red, Green, Blue]
  option_value: [red, green, blue]
- style: checkbox
  position: {x: 100, y: 70, width: 150, height: 20}
  variable: active
  text: Active
- style: pushbutton
  position: {x: 100, y: 100, width: 100, height: 28}
  text: Submit
- style: text
  position: {x: 100, y: 140, width: 300, height: 20}
  variable: status
"""

    def test_all_widgets_build(self, make_gui):
        gui = make_gui(
            self.CONFIG,
            {
                "form": {
                    "name": "test",
                    "color": "green",
                    "active": True,
                    "status": "Ready",
                }
            },
        )
        assert gui.getvar("form", "name") == "test"
        assert gui.getvar("form", "color") == "green"
        assert gui.getvar("form", "active") is True
        assert gui.getvar("form", "status") == "Ready"

    def test_update_all(self, make_gui):
        gui = make_gui(
            self.CONFIG,
            {"form": {"name": "", "color": "red", "active": False, "status": ""}},
        )
        gui.setvar("form", "name", "updated")
        gui.setvar("form", "color", "blue")
        gui.setvar("form", "active", True)
        gui.setvar("form", "status", "Done")

        assert gui.getvar("form", "name") == "updated"
        assert gui.getvar("form", "color") == "blue"
        assert gui.getvar("form", "active") is True
        assert gui.getvar("form", "status") == "Done"
