from abc import ABC, abstractmethod

class IEventListener(ABC):

    @abstractmethod
    def before(self, event):
        pass

    @abstractmethod
    def after(self, event):
        pass

    @abstractmethod
    def onSuccess(self, event):
        pass

    @abstractmethod
    def onFailure(self, event):
        pass

    @abstractmethod
    def onMissed(self, event):
        pass

    @abstractmethod
    def onMaxInstances(self, event):
        pass