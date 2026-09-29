import os
from ignis.gobject import IgnisGObject, IgnisProperty
from ignis import utils
from .constants import SYS_BACKLIGHT


class BacklightDevice(IgnisGObject):
    """
    A backlight device.
    """

    def __init__(self, device_name: str):
        super().__init__()
        self._device_name = device_name
        self._brightness: int = -1
        self._max_brightness: int = -1

        self._PATH_TO_BRIGHTNESS = os.path.join(
            SYS_BACKLIGHT, device_name, "brightness"
        )
        self._PATH_TO_MAX_BRIGHTNESS = os.path.join(
            SYS_BACKLIGHT, device_name, "max_brightness"
        )

        with open(self._PATH_TO_MAX_BRIGHTNESS) as backlight_file:
            self._max_brightness = int(backlight_file.read().strip())

        utils.FileMonitor(
            path=self._PATH_TO_BRIGHTNESS,
            callback=lambda x, path, event_type: self.__sync_brightness()
            if event_type != "changed"  # "changed" event is called multiple times
            else None,
        )

        self.__sync_brightness()

    def __sync_brightness(self) -> None:
        with open(self._PATH_TO_BRIGHTNESS) as backlight_file:
            self._brightness = int(backlight_file.read().strip())

        self.notify("brightness")

    @IgnisProperty
    def device_name(self) -> str:
        """
        The name of the directory in ``/sys/class/backlight``.
        """
        return self._device_name

    @IgnisProperty
    def max_brightness(self) -> int:
        """
        The maximum brightness allowed by the device.
        """
        return self._max_brightness

    @IgnisProperty
    def brightness(self) -> int:
        """
        The current brightness of the device.
        """
        return self._brightness

    @brightness.setter
    def brightness(self, value: int) -> None:
        value = max(0, min(value, self._max_brightness))

        with open(self._PATH_TO_BRIGHTNESS, "w") as backlight_file:
            backlight_file.write(str(value))

        self.__sync_brightness()

    async def set_brightness_async(self, value: int) -> None:
        value = max(0, min(value, self._max_brightness))

        with open(self._PATH_TO_BRIGHTNESS, "w") as backlight_file:
            backlight_file.write(str(value))

        self.__sync_brightness()
