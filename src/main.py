### Runs main program ###

import sys
from PyQt6.QtWidgets import QApplication
from qt_live_input import AudioVisualizer


def main():
    app = QApplication(sys.argv)
    window = AudioVisualizer()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()