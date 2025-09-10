from dataclasses import asdict, dataclass

@dataclass
class I_Account:
    id: str
    password: str
    name: str | None = None
