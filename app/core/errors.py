class DomainError(Exception):
    status_code = 400

    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(detail)


class NotFoundError(DomainError):
    status_code = 404


class ConflictError(DomainError):
    status_code = 409


class RuleViolationError(DomainError):
    status_code = 422