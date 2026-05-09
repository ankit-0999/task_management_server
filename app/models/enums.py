import enum

class UserRole(str, enum.Enum):
    ADMIN = "Admin"
    MEMBER = "Member"

class TaskStatus(str, enum.Enum):
    TODO = "Todo"
    IN_PROGRESS = "In-Progress"
    COMPLETED = "Completed"
    OVERDUE = "Overdue"
    ON_HOLD = "On-Hold"

class ProjectStatus(str, enum.Enum):
    TODO = "Todo"
    IN_PROGRESS = "In-Progress"
    COMPLETED = "Completed"
    ON_HOLD = "On-Hold"
