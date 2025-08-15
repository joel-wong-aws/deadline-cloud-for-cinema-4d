# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
import os

from qtpy.QtCore import QSize, Qt  # type: ignore
from qtpy.QtWidgets import (  # type: ignore
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from deadline.client.ui.widgets.job_timeouts_widget import TimeoutEntryWidget, TimeoutTableWidget

from ...takes import TakeSelection
from ...constants import ErrorChecking, FreezeDetection

"""
UI widgets for the Scene Settings tab.
"""


class FileSearchLineEdit(QWidget):
    """
    Widget used to contain a line edit and a button which opens a file search box.
    """

    def __init__(self, file_format=None, directory_only=False, parent=None):
        super().__init__(parent=parent)

        if directory_only and file_format is not None:
            raise ValueError("")

        self.file_format = file_format
        self.directory_only = directory_only

        lyt = QHBoxLayout(self)
        lyt.setContentsMargins(0, 0, 0, 0)

        self.edit = QLineEdit(self)
        self.edit.setMaxLength(32767)
        self.btn = QPushButton("...", parent=self)
        self.btn.setMaximumSize(QSize(100, 40))
        self.btn.clicked.connect(self.get_file)

        lyt.addWidget(self.edit)
        lyt.addWidget(self.btn)

    def get_file(self):
        """
        Open a file picker to allow users to choose a file.
        """
        if self.directory_only:
            new_txt = QFileDialog.getExistingDirectory(
                self,
                "Open Directory",
                self.edit.text(),
                QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks,
            )
        else:
            new_txt = QFileDialog.getOpenFileName(self, "Select File", self.edit.text())

        if new_txt:
            self.edit.setText(new_txt)

    def setText(self, txt: str) -> None:  # pylint: disable=invalid-name
        """
        Sets the text of the internal line edit
        """
        self.edit.setText(txt)

    def text(self) -> str:
        """
        Retrieves the text from the internal line edit.
        """
        return self.edit.text()


class SceneSettingsWidget(QWidget):
    """
    Widget containing all top level scene settings.
    """

    def __init__(self, initial_settings, parent=None):
        super().__init__(parent=parent)

        self.developer_options = (
            os.environ.get("DEADLINE_ENABLE_DEVELOPER_OPTIONS", "").upper() == "TRUE"
        )
        # Save the two lists of selectable cameras
        self._build_ui(initial_settings)
        self._configure_settings(initial_settings)

    def _build_ui(self, settings):
        lyt = QGridLayout(self)

        widget_number = 1

        self.op_path_chck = QCheckBox("Override Output Path", self)
        self.op_path_txt = FileSearchLineEdit(directory_only=True)
        lyt.addWidget(self.op_path_chck, widget_number, 0)
        lyt.addWidget(self.op_path_txt, widget_number, 1)
        widget_number += 1
        self.op_path_chck.stateChanged.connect(self.activate_path_changed)

        self.op_multi_path_chck = QCheckBox("Override Multi-Pass Path", self)
        self.op_multi_path_txt = FileSearchLineEdit(directory_only=True)
        lyt.addWidget(self.op_multi_path_chck, widget_number, 0)
        lyt.addWidget(self.op_multi_path_txt, widget_number, 1)
        widget_number += 1
        self.op_multi_path_chck.stateChanged.connect(self.activate_multi_path_changed)

        self.layers_box = QComboBox(self)
        layer_items = [
            (TakeSelection.MAIN, "Main Take"),
            (TakeSelection.ALL, "All Takes"),
            (TakeSelection.MARKED, "Marked Takes"),
            (TakeSelection.CURRENT, "Current Take"),
        ]
        for layer_value, text in layer_items:
            self.layers_box.addItem(text, layer_value)
        lyt.addWidget(QLabel("Takes"), widget_number, 0)
        lyt.addWidget(self.layers_box, widget_number, 1)
        widget_number += 1

        self.frame_override_chck = QCheckBox("Override Frame Range", self)
        self.frame_override_txt = QLineEdit(self)
        self.frame_override_txt.setMaxLength(32767)
        lyt.addWidget(self.frame_override_chck, widget_number, 0)
        lyt.addWidget(self.frame_override_txt, widget_number, 1)
        widget_number += 1
        self.frame_override_chck.stateChanged.connect(self.activate_frame_override_changed)

        self.activate_error_checking_chck = QCheckBox("Activate automatic error checking", self)
        lyt.addWidget(self.activate_error_checking_chck, widget_number, 0)
        widget_number += 1

        self.activate_freeze_detection_chck = QCheckBox("Activate automatic freeze detection", self)

        self.hours_box = QSpinBox(self, minimum=0, maximum=719)
        self.hours_box.setSuffix(" hours")
        self.hours_box.setFixedWidth(90)

        self.minutes_box = QSpinBox(self, minimum=0, maximum=59)
        self.minutes_box.setSuffix(" minutes")
        self.minutes_box.setFixedWidth(90)

        self.seconds_box = QSpinBox(self, minimum=0, maximum=59)
        self.seconds_box.setSuffix(" seconds")
        self.seconds_box.setFixedWidth(90)

        self.freeze_detection = TimeoutEntryWidget(
            "Activate Automatic Freeze Detection",
            "Amount of time to wait before failing due to lack of progress being reported.",
        )
        lyt.addWidget(self.freeze_detection, widget_number, 0, 1, 2)
        widget_number += 1

        self.timeout_settings_box = TimeoutTableWidget(timeouts=settings.timeouts, parent=self)
        lyt.addWidget(self.timeout_settings_box, widget_number, 0, 1, 2)
        widget_number += 1

        # Create a group box for the export job bundle option
        export_group_box = QGroupBox("Cinema 4D submission options", self)
        export_layout = QVBoxLayout(export_group_box)

        self.export_job_bundle_chck = QCheckBox(
            "Save Cinema 4D project with assets before submission", self
        )
        export_layout.addWidget(self.export_job_bundle_chck)

        warning_label = QLabel(
            "Prevents missing file errors during rendering by creating a temporary copy of your project with all assets "
            "and fixing file paths before submission. Uses more disk space and submission time."
        )
        warning_label.setWordWrap(True)
        export_layout.addWidget(warning_label)

        lyt.addWidget(export_group_box, widget_number, 0, 1, 2)
        widget_number += 1

        if self.developer_options:
            self.include_adaptor_wheels = QCheckBox(
                "Developer Option: Include Adaptor Wheels", self
            )
            lyt.addWidget(self.include_adaptor_wheels, widget_number, 0)
            widget_number += 1

        lyt.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding), widget_number, 0)
        widget_number += 1

    def _configure_settings(self, settings):
        self.op_path_chck.setChecked(settings.override_output_path)
        self.op_path_txt.setEnabled(settings.override_output_path)
        self.op_multi_path_chck.setChecked(settings.override_multi_pass_path)
        self.op_multi_path_txt.setEnabled(settings.override_multi_pass_path)
        self.op_path_txt.setText(settings.output_path)
        self.op_multi_path_txt.setText(settings.multi_pass_path)
        self.frame_override_chck.setChecked(settings.override_frame_range)
        self.frame_override_txt.setEnabled(settings.override_frame_range)
        self.frame_override_txt.setText(settings.frame_list)
        self.activate_error_checking_chck.setChecked(bool(int(settings.activate_error_checking)))
        self.freeze_detection.set_enabled(bool(int(settings.activate_freeze_detection)))
        self.freeze_detection.set_timeout(int(settings.freeze_detection_time))

        index = self.layers_box.findData(settings.take_selection)
        if index >= 0:
            self.layers_box.setCurrentIndex(index)

        self.export_job_bundle_chck.setChecked(settings.export_job_bundle_to_temp)

        if self.developer_options:
            self.include_adaptor_wheels.setChecked(settings.include_adaptor_wheels)

    def update_settings(self, settings):
        """
        Update a scene settings object with the latest values.
        """
        settings.output_path = self.op_path_txt.text()
        settings.multi_pass_path = self.op_multi_path_txt.text()

        settings.override_output_path = self.op_path_chck.isChecked()
        settings.override_multi_pass_path = self.op_multi_path_chck.isChecked()

        settings.override_frame_range = self.frame_override_chck.isChecked()
        settings.frame_list = self.frame_override_txt.text()

        settings.take_selection = self.layers_box.currentData()

        settings.activate_error_checking = (
            ErrorChecking.ACTIVATE.value
            if self.activate_error_checking_chck.isChecked()
            else ErrorChecking.DEACTIVATE.value
        )

        settings.activate_freeze_detection = (
            FreezeDetection.ACTIVATE.value
            if self.freeze_detection.checkbox.isChecked()
            else FreezeDetection.DEACTIVATE.value
        )
        settings.freeze_detection_time = self.freeze_detection.get_timeout_seconds()

        self.timeout_settings_box.update_settings(settings.timeouts)

        settings.export_job_bundle_to_temp = self.export_job_bundle_chck.isChecked()

        if self.developer_options:
            settings.include_adaptor_wheels = self.include_adaptor_wheels.isChecked()
        else:
            settings.include_adaptor_wheels = False

    def activate_frame_override_changed(self, state):
        """
        Set the activated/deactivated status of the Frame override text box
        """
        self.frame_override_txt.setEnabled(Qt.CheckState(state) == Qt.Checked)

    def activate_path_changed(self, state):
        self.op_path_txt.setEnabled(Qt.CheckState(state) == Qt.Checked)

    def activate_multi_path_changed(self, state):
        self.op_multi_path_txt.setEnabled(Qt.CheckState(state) == Qt.Checked)

    def activate_freeze_detection_changed(self, state):
        enabled = Qt.CheckState(state) == Qt.Checked
        self.hours_box.setEnabled(enabled)
        self.minutes_box.setEnabled(enabled)
        self.seconds_box.setEnabled(enabled)
