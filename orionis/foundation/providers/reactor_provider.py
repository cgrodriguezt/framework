from __future__ import annotations
from orionis.container.providers.deferrable_provider import DeferrableProvider
from orionis.container.providers.service_provider import ServiceProvider
from orionis.console.contracts.reactor import IReactor
from orionis.console.core.reactor import Reactor

class ReactorProvider(ServiceProvider, DeferrableProvider):

	def register(self) -> None:
		"""
		Register the reactor management service in the application container.

		Registers the `IReactor` interface as a singleton bound to the `Reactor`
		implementation in the application's dependency injection container. An alias
		is provided for explicit retrieval.

		Parameters
		----------
		self : ReactorProvider
			Instance of the ReactorProvider.

		Returns
		-------
		None
			This method does not return a value. It registers the service in the
			application container.
		"""
		# Bind IReactor to Reactor as a singleton with an alias for retrieval.
		self.app.singleton(
			IReactor,
			Reactor,
			alias="x-orionis.console.contracts.reactor.IReactor",
		)

	def provides(self) -> list[type]:
		"""
		Specify the services provided by the ReactorProvider.

		Returns a list of service types that the ReactorProvider registers in the
		application container, indicating it provides the `IReactor` service.

		Parameters
		----------
		self : ReactorProvider
			Instance of the ReactorProvider.

		Returns
		-------
		list of type
			List containing the `IReactor` type, indicating the provider supplies
			the reactor management service.
		"""
		# Indicate that this provider supplies the IReactor service.
		return [IReactor]
