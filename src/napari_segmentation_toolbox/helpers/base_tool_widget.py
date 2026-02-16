import napari
from psygnal import Signal
from qtpy.QtWidgets import (
    QWidget,
)


class BaseToolWidget(QWidget):
    """Base widget that listens to the napari layer list and communicates whether the
    current active layer is of the correct layer type."""

    update_status = Signal()
    layer_updated = Signal(str)

    def __init__(
        self,
        viewer: "napari.viewer.Viewer",
        layer_type: tuple,
        mode: str = "set_layer",
    ) -> None:
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
        self.layer_type = layer_type
        self.layer = None
        self.mode = mode

        self.viewer.layers.selection.events.active.connect(
            self._on_selection_changed
        )

    def _on_selection_changed(self):
        """Listen to the napari layer list updates, and send a signal to notify the parent
        widget if a single layer is selected that is of the correct type. Either update
        the layer directly, or simply emit the layer name, and let the parent widget
        process this."""

        if (
            len(self.viewer.layers.selection) == 1
        ):  # Only consider single layer selection
            selected_layer = self.viewer.layers.selection.active

            if self.mode == "set_layer":
                if isinstance(selected_layer, self.layer_type):
                    self.layer = selected_layer
                else:
                    self.layer = None

                self.update_status.emit()

            elif self.mode == "emit_layer_name":
                if isinstance(selected_layer, self.layer_type):
                    name = selected_layer.name
                else:
                    name = None

                self.layer_updated.emit(name)
