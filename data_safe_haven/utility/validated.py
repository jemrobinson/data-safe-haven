"""Implement a self-validating attribute using a descriptor"""
from collections.abc import Callable
from typing import Generic, TypeVar, cast

from chili import TypeDecoder

T = TypeVar("T")


class Validated(Generic[T]):
    """A self-validating attribute using a descriptor"""

    def __init__(
        self, on_update: Callable[[T | None, T | None], bool] | None = None
    ) -> None:
        """Descriptor to provide validation when value is changed

        NB. this class is a descriptor (https://docs.python.org/3/howto/descriptor.html)
        and is therefore only functional when used as an attribute.

        Args:
            on_update: A function that compares the old and new values on each update
        """
        self.on_update: Callable[[T | None, T | None], bool] | None = on_update

    def __set_name__(self, _: object, name: str) -> None:
        """Track the name of this attribute

        This is needed when we want to set the value of an instance

        Args:
            instance: the object that this variable belongs to
            name: the attribute name of this variable
        """
        self.name = name

    def __get__(
        self, instance: object | None, instance_type: type[object] | None
    ) -> "Validated[T]" | T:
        """Get the stored value

        Args:
            instance: the object that this variable belongs to
            instance_type: the type of instance

        Returns:
            The stored value
        """
        try:
            return cast(T, instance.__dict__[self.name])
        except (AttributeError, KeyError):
            return self

    def __set__(self, instance: object, value: T | None) -> None:
        """Set the stored value

        Validate the provided value using the validator function

        Args:
            instance: the class that this instance variable belongs to
            value: the value to store

        Raises:
            An exception if the validation fails
        """
        if self.on_update:
            old = (
                cast(T, instance.__dict__[self.name])
                if self.name in instance.__dict__
                else None
            )
            if self.on_update(old, value):
                instance.__dict__[self.name] = value
                self.last_type = type(value)


class DecoderValidated(TypeDecoder, Generic[T]):
    """A chili type decoder that returns its input"""

    def decode(self, value: T) -> T:
        return value
