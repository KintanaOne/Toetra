# /forml/grammar/official_contents/utils.py

class EnumMixin:
    @classmethod
    def from_str(cls, name: str):
        """
        
        """
        normalized = name.strip('"').upper()
        for member in cls:
            if member.value.upper() == normalized:
                return member
        raise ValueError(f"{cls.__name__} inconnu : {name}")
