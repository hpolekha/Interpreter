from abc import ABC, abstractmethod

class INodeVisitor(ABC):
    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def raise_error(self, msg, code=None):
        pass


