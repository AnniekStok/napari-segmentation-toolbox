from contextlib import suppress

from psygnal import Signal
from qtpy.QtCore import QObject
from qtpy.QtWidgets import (
    QWidget,
)


def get_layer_manager(viewer):
    window = viewer.window

    if not hasattr(window, "_layer_manager"):
        window._layer_manager = LayerManager(viewer)

    return window._layer_manager


class LayerManager(QObject):
    layer_updated = Signal(object)

    def __init__(self, viewer):
        super().__init__()
        self.viewer = viewer
        self._current_layer = None

        self.viewer.layers.selection.events.active.connect(
            self._on_selection_changed
        )

    def _on_selection_changed(self):
        if len(self.viewer.layers.selection) == 1:
            layer = self.viewer.layers.selection.active
        else:
            layer = None

        if layer is self._current_layer:
            return

        self._current_layer = layer
        self.layer_updated.emit(layer)


class BaseToolWidget(QWidget):
    """Base widget that listens to the napari layer list and communicates whether the
    current active layer is of the correct layer type."""

    update_status = Signal()
    layer_updated = Signal(str)

    def __init__(self, viewer, layer_type, mode="set_layer"):
        """
        Initialize base widget.
        Args:
            viewer (napari.viewer.Viewer): napari viewer holding the layers
            layer_type (tuple): the layer type(s) the widget should react to.
            mode (str, one of "set_layer", "emit_layer_name"): whether to directly
            overwrite the layer, or emit the layer name so that the parent widget can
            handle it.
        """

        super().__init__()
        self.viewer = viewer
        self.layer_manager = get_layer_manager(viewer)
        self.layer_type = layer_type
        self.mode = mode
        self.layer = None

        self.layer_manager.layer_updated.connect(self._on_layer_changed)

    def _on_layer_changed(self, selected_layer):
        """Send a signal to notify the parent widget if a single layer is selected that is
        of the correct type. Either update the layer directly, or simply emit the layer
        name, and let the parent widget process this."""
        if self.mode == "set_layer":
            self.layer = (
                selected_layer
                if isinstance(selected_layer, self.layer_type)
                else None
            )
            self.update_status.emit()

        elif self.mode == "emit_layer_name":
            name = (
                selected_layer.name
                if isinstance(selected_layer, self.layer_type)
                else None
            )
            self.layer_updated.emit(name)

    def closeEvent(self, event):
        with suppress(ValueError):
            self.layer_manager.layer_updated.disconnect(self._on_layer_changed)
        super().closeEvent(event)
