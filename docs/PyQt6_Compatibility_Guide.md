# PyQt6 Compatibility Guide

This guide covers common compatibility issues when working with PyQt6 in the ConsultEase application, particularly when upgrading from PyQt5 or adapting code examples.

## Table of Contents

1. [Introduction](#introduction)
2. [Common Syntax Changes](#common-syntax-changes)
3. [Import Changes](#import-changes)
4. [Signal and Slot Changes](#signal-and-slot-changes)
5. [Layout Changes](#layout-changes)
6. [Keyboard Handling](#keyboard-handling)

## Introduction

PyQt6 introduces several breaking changes compared to PyQt5. This guide documents the most common issues encountered in the ConsultEase application and how to fix them.

## Common Syntax Changes

### Enum Changes

PyQt6 uses a more explicit enum system than PyQt5. Many previously flat enums now use a nested structure.

#### Font Weight

**PyQt5:**
```python
font = QFont("Arial", 12, QFont.Bold)
```

**PyQt6 (correct):**
```python
font = QFont("Arial", 12, QFont.Weight.Bold)
```

#### Size Policy

**PyQt5:**
```python
widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
```

**PyQt6 (correct):**
```python
widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
```

#### Alignment

**PyQt5:**
```python
label.setAlignment(Qt.AlignCenter)
```

**PyQt6 (correct):**
```python
label.setAlignment(Qt.AlignmentFlag.AlignCenter)
```

#### Orientation

**PyQt5:**
```python
splitter = QSplitter(Qt.Horizontal)
```

**PyQt6 (correct):**
```python
splitter = QSplitter(Qt.Orientation.Horizontal)
```

#### Frame Style

**PyQt5:**
```python
frame.setFrameShape(QFrame.StyledPanel)
frame.setFrameShadow(QFrame.Raised)
```

**PyQt6 (correct):**
```python
frame.setFrameShape(QFrame.Shape.StyledPanel)
frame.setFrameShadow(QFrame.Shadow.Raised)
```

## Import Changes

Some classes have moved between modules in PyQt6. Make sure to use the correct import statements.

**Common PyQt6 imports:**
```python
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QApplication)
from PyQt6.QtGui import (QFont, QPixmap, QIcon, QColor)
from PyQt6.QtCore import (Qt, QTimer, pyqtSignal, pyqtSlot)
```

## Signal and Slot Changes

PyQt6 has made some changes to signal and slot connections:

1. `PyQt6.QtCore.pyqtSlot` replaces `QtCore.pyqtSlot`
2. Signal connection syntax remains compatible

**Example:**
```python
# Defining a custom signal
my_signal = pyqtSignal(str)

# Connecting a signal to a slot
button.clicked.connect(self.handle_click)

# Slot method
@pyqtSlot()
def handle_click(self):
    print("Button clicked")
```

## Layout Changes

Layout management in PyQt6 is largely the same as PyQt5, but there are some differences in enum usage:

**PyQt5:**
```python
spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
```

**PyQt6 (correct):**
```python
spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
```

## Keyboard Handling

PyQt6 has some changes in keyboard handling, particularly for on-screen keyboards:

1. `QApplication` instance is needed for keyboard handling
2. Keyboard handler needs proper D-Bus integration for systems like Squeekboard

**Example keyboard handler initialization:**
```python
# In main.py
app = QApplication(sys.argv)
app.keyboard_handler = KeyboardHandler(app)

# Accessing keyboard handler in widgets
keyboard_button = QPushButton("Keyboard")
keyboard_button.clicked.connect(lambda: QApplication.instance().keyboard_handler.toggle_keyboard())
```

## Additional Resources

- [PyQt6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [Qt6 Documentation](https://doc.qt.io/qt-6/)
- [Porting from PyQt5 to PyQt6](https://www.riverbankcomputing.com/static/Docs/PyQt6/pyqt_differences.html) 