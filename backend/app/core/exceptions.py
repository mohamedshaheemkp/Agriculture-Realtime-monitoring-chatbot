class AppError(Exception):
    """Base error class for the application."""
    def __init__(self, message, status_code=500, payload=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['success'] = False
        rv['error'] = {
            'code': self.__class__.__name__,
            'message': self.message
        }
        return rv

class ModelNotFoundError(AppError):
    def __init__(self, message="AI Model not found or failed to load."):
        super().__init__(message, status_code=500)

class SensorReadError(AppError):
    def __init__(self, message="Failed to read from sensors."):
        super().__init__(message, status_code=503)

class ValidationError(AppError):
    def __init__(self, message="Invalid input data."):
        super().__init__(message, status_code=400)
