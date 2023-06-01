import yaml
from pydantic import BaseModel as PydanticBaseModel


class BaseModel(PydanticBaseModel):
    def from_json(self, json_str: str):
        return self.parse_raw(json_str)

    def to_json(self) -> str:
        return super().json(indent=4, ensure_ascii=False)

    def from_yaml(self, yaml_str: str):
        data = yaml.load(yaml_str, Loader=yaml.FullLoader)
        json_str = yaml.dump(data)
        return self.parse_raw(json_str)

    def to_yaml(self) -> str:
        data = self.dict()
        return yaml.dump(data, indent=4)

    def __str__(self) -> str:
        return get_model_fields(self, indent=0)


def get_model_fields(self, indent: int = 0) -> str:
    result = ""
    for key, value in self.dict().items():
        if isinstance(value, BaseModel):
            result += (
                f"{' ' * indent}{key}:\n{self.get_model_fields(value, indent + 2)}"
            )
        elif isinstance(value, list):
            result += f"{' ' * indent}{key}:\n"
            for item in value:
                if isinstance(item, BaseModel):
                    result += self.get_model_fields(item, indent + 2)
                else:
                    result += f"{' ' * (indent + 2)}{item}\n"
        else:
            result += f"{' ' * indent}{key}: {value}\n"
    return result
