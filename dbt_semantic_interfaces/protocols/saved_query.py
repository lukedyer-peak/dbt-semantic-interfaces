from abc import abstractmethod
from typing import Optional, Protocol, Sequence

from dbt_semantic_interfaces.protocols.metadata import Metadata
from dbt_semantic_interfaces.protocols.where_filter import WhereFilter


class SavedQuery(Protocol):
    """Represents a query that the user wants to run repeatedly."""

    @property
    @abstractmethod
    def metadata(self) -> Optional[Metadata]:  # noqa: D
        pass

    @property
    @abstractmethod
    def name(self) -> str:  # noqa: D
        pass

    @property
    @abstractmethod
    def description(self) -> Optional[str]:  # noqa: D
        pass

    @property
    @abstractmethod
    def metrics(self) -> Sequence[str]:  # noqa: D
        pass

    @property
    @abstractmethod
    def group_bys(self) -> Sequence[str]:  # noqa: D
        pass

    @property
    @abstractmethod
    def where(self) -> Sequence[WhereFilter]:  # noqa: D
        pass

    @property
    @abstractmethod
    def label(self) -> Optional[str]:
        """Returns a string representing a human readable label for the saved query."""
        pass
