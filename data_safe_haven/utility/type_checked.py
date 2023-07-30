"""A descriptor attribute that enforces type checking"""
from typing import Any, Generic, TypeVar, cast

from chili import TypeDecoder, TypeEncoder

from data_safe_haven.exceptions import DataSafeHavenParameterError

T = TypeVar("T")


class UnsetType:
    pass


Unset = UnsetType()


class TypeChecked(Generic[T]):
    """A descriptor attribute that enforces type checking"""

    def __init__(
        self,
        *,
        default: T | UnsetType = Unset,
    ) -> None:
        """Descriptor to provide validation when value is changed

        NB. this class is a descriptor (https://docs.python.org/3/howto/descriptor.html)
        and is therefore only functional when used as an attribute.
        """
        self.default = default

    def check_type(self, value: Any) -> T:
        wrapped_type = object.__getattribute__(self, "__orig_class__").__args__[0]
        try:
            if not isinstance(value, wrapped_type):
                msg = f"Invalid type for '{self.name}': '{value}' is not a {wrapped_type.__name__}."
                raise DataSafeHavenParameterError(msg)
        except TypeError as exc:
            msg = f"Invalid type for '{self.name}': could not determine whether '{value}' is a {wrapped_type}.\n{exc}"
            raise DataSafeHavenParameterError(msg) from exc
        return cast(T, value)

    def __set_name__(self, _: object, name: str) -> None:
        """Track the name of this attribute

        This is needed when we want to set the value of an instance

        Args:
            instance: the object that this variable belongs to
            name: the attribute name of this variable
        """
        self.name = name

    def __get__(
        self, instance: object | None, _: type[object] | None
    ) -> "TypeChecked[T]" | T:
        """Get the stored value

        Args:
            instance: the object that this variable belongs to
            _: (unused) the type of instance

        Returns:
            With an instance: the instance value
            With no instance: the default value (if one exists) or this object if not
        """
        try:
            value = instance.__dict__[self.name]
            return self.check_type(value)
        except (AttributeError, DataSafeHavenParameterError, KeyError):
            if not isinstance(self.default, UnsetType):
                return self.default
            return self

    def __set__(self, instance: object, value: T | "TypeChecked[T]") -> None:
        """Set the stored value

        Validate the provided value using the validator function

        Args:
            instance: the class that this instance variable belongs to
            value: the value to store

        Raises:
            A DataSafeHavenParameterError if the validation fails
        """
        # print(f"__set__ check_type {value} {self.name} {self}")
        if isinstance(value, TypeChecked):
            # print(f"{self.name}: adding TypeChecked")
            instance.__dict__[self.name] = value
        else:
            # print(f"{self.name}: adding value {value} after TypeChecking")
            instance.__dict__[self.name] = self.check_type(value)


class DecoderTypeChecked(TypeDecoder, Generic[T]):
    """A chili type decoder that returns its input"""

    def decode(self, value: T) -> T:
        return value


class EncoderTypeChecked(TypeEncoder, Generic[T]):
    def encode(self, value: T) -> T:
        return value
