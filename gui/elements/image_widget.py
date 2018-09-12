# pythonprogramminglanguage.com
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGridLayout, QWidget, QSlider, QMenuBar

from vispy.scene import SceneCanvas

from .image_container import ImageContainer
from .panzoom import PanZoomCamera

from ..util import is_rgb


class ImageViewerWidget(QWidget):
    """Image-based PyQt5 widget.

    Parameters
    ----------
    image : np.ndarray
        Image contained by the widget.
    meta : dict
        Image metadata.
    containing_window : PyQt5.QWindow, optional
        Window that contains the widget.
    """
    def __init__(self, image, meta, parent=None):
        super().__init__(parent=parent)

        self.image = image
        self.meta = meta

        self.point = [0] * image.ndim
        self.axis0 = image.ndim - 2 - is_rgb(meta)
        self.axis1 = image.ndim - 1 - is_rgb(meta)
        self.slider_index_map = {}

        layout = QGridLayout()
        self.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0);
        layout.setColumnStretch(0, 4)

        row = 0

        self.canvas = SceneCanvas(keys=None, vsync=True)
        self.view = self.canvas.central_widget.add_view()

        # Set 2D camera (the camera will scale to the contents in the scene)
        self.view.camera = PanZoomCamera(aspect=1)
        # flip y-axis to have correct aligment
        self.view.camera.flip = (0, 1, 0)
        self.view.camera.set_range()
        # view.camera.zoom(0.1, (250, 200))

        self.image_container = ImageContainer(image, meta, self.view,
                                              self.canvas.update)

        layout.addWidget(self.canvas.native, row, 0)
        layout.setRowStretch(row, 1)
        row += 1

        for axis in range(image.ndim - is_rgb(meta)):
            if axis != self.axis0 and axis != self.axis1:
                self.add_slider(layout, row, axis, image.shape[axis])

                layout.setRowStretch(row, 4)
                row += 1

        self.update_image()

    def add_slider(self, grid, row,  axis, length):
        """Adds a slider to the given grid.

        Parameters
        ----------
        grid : PyQt5.QGridLayout
            Grid layout to add the slider to.
        row : int
            Row in which to add the slider.
        axis : int
            Axis that this slider controls.
        length : int
            Maximum length of the slider.
        """
        slider = QSlider(Qt.Horizontal)
        slider.setFocusPolicy(Qt.StrongFocus)
        slider.setTickPosition(QSlider.TicksBothSides)
        slider.setMinimum(0)
        slider.setMaximum(length-1)
        slider.setFixedHeight(17)
        slider.setTickPosition(QSlider.NoTicks)
        # tick_interval = int(max(8,length/8))
        # slider.setTickInterval(tick_interval)
        slider.setSingleStep(1)
        grid.addWidget(slider, row, 0)

        def value_changed():
            self.point[axis] = slider.value()
            self.update_image()

        slider.valueChanged.connect(value_changed)

    def update_image(self):
        """Updates the contained image."""
        index = list(self.point)
        index[self.axis0] = slice(None)
        index[self.axis1] = slice(None)

        if is_rgb(self.meta):
            index[-1] = slice(None)

        sliced_image = self.image[tuple(index)]

        self.image_container.set_image(sliced_image, self.meta)

    @property
    def cmap(self):
        """string: Color map.
        """
        return self.image_container.cmap

    @cmap.setter
    def cmap(self, cmap):
        self.image_container.cmap = cmap
