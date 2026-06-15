from sunbot.std import ApplicationError, NetworkError, PlatformError


class TestApplicationError:
    def test_base_maps_to_500(self) -> None:
        assert ApplicationError().to_http_status_code() == 500

    def test_subclass_overrides_status(self) -> None:
        class NotFound(ApplicationError):
            status_code = 404

        assert NotFound().to_http_status_code() == 404


class TestNetworkError:
    def test_is_platform_error(self) -> None:
        assert issubclass(NetworkError, PlatformError)

    def test_format_traceback_includes_message(self) -> None:
        try:
            raise NetworkError("upstream down")
        except NetworkError as e:
            formatted = e.format_traceback()
        assert "NetworkError" in formatted
        assert "upstream down" in formatted
