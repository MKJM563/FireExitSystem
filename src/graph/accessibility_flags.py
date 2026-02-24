class AccessibilityFlags:
    def __init__(self, wheelchair: bool, stretcher: bool, general: bool) -> None:
        self._wheelchair_accessible: bool = wheelchair
        self._stretcher_accessible: bool = stretcher
        self._general_access: bool = general

    @property
    def wheelchair_accessible(self) -> bool:
        return self._wheelchair_accessible

    @property
    def stretcher_accessible(self) -> bool:
        return self._stretcher_accessible

    @property
    def general_access(self) -> bool:
        return self._general_access

    def matches(self, requirements: "AccessibilityFlags") -> bool:
        """Return True if this object satisfies all required accessibility flags."""
        if requirements.wheelchair_accessible and not self._wheelchair_accessible:
            return False
        if requirements.stretcher_accessible and not self._stretcher_accessible:
            return False
        if requirements.general_access and not self._general_access:
            return False
        return True

    def __repr__(self) -> str:
        return (
            f"AccessibilityFlags(wheelchair={self._wheelchair_accessible}, "
            f"stretcher={self._stretcher_accessible}, general={self._general_access})"
        )
