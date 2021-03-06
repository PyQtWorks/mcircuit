from PySide2.QtCore import QTimer
from PySide2.QtWidgets import QApplication, QMainWindow, QWidget, QAction, QToolBar, QLabel, QTreeWidget, \
    QTreeWidgetItem, QDockWidget
from version import format_version
from descriptors import *
from elements import *
from time import perf_counter


def make_title():
    return f'mcircuit {format_version()}'


ELEMENTS = {

}


class ElementTree(QTreeWidget):
    def __init__(self):
        super().__init__()

        self.setHeaderHidden(True)
        self.setColumnCount(1)

    def create_from_dict(self, d):
        for category in d:
            category_item = QTreeWidgetItem()
            category_item.setText(0, category)

            for elem_name in d[category]:
                it = QTreeWidgetItem()
                it.setText(0, elem_name)
                category_item.addChild(it)

            self.addTopLevelItem(category_item)


if __name__ == "__main__":
    app = QApplication()
    w = QMainWindow()
    w.setMinimumSize(640, 480)

    elems = ElementTree()
    elems.create_from_dict(ELEMENTS)
    elems.expandAll()
    dw = QDockWidget()
    dw.setWidget(elems)
    dw.setWindowTitle('Elements')
    dw.setFeatures(QDockWidget.DockWidgetMovable |
                   QDockWidget.DockWidgetFloatable)
    w.addDockWidget(Qt.LeftDockWidgetArea, dw)

    sim = Simulator()
    g = Gate('or', 1, 2, False)
    g.name = 'gate'
    sim.root = g
    t = QTimer(w)

    ed = SchematicEditor()
    w.setCentralWidget(ed)

    edd = None

    ticks = 0

    def _on_timer():
        global ticks
        sim.burst()
        ticks += BURST_SIZE
        ed.update()

    t.timeout.connect(_on_timer)

    action = QAction('Simulate')
    action.setCheckable(True)

    def _handle_sim_action():
        simulating = action.isChecked()
        if simulating:
            sim.init()
            t.start(1000 / 60)
            benc_timer.start(1000)
        else:
            lbl.setText('')
            sim.cleanup()
            t.stop()
            benc_timer.stop()

    action.changed.connect(_handle_sim_action)
    toolbar = QToolBar()

    lbl = QLabel()

    benc_timer = QTimer(w)

    def _on_bench():
        global ticks
        lbl.setText(f'Frequency: {ticks} Hz')
        ticks = 0

    benc_timer.timeout.connect(_on_bench)

    toolbar.addAction(action)
    toolbar.addSeparator()
    toolbar.addWidget(lbl)
    w.addToolBar(toolbar)

    w.setWindowTitle(make_title())
    w.show()
    app.exec_()
