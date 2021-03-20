from abc import ABC, abstractmethod

class INode(ABC):
    @abstractmethod
    def accept(self, visitor):
        pass


