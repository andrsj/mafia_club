from zlo.adapters.infrastructure import MessageBus
from zlo.domain.events import (
    CreateOrUpdateGame,
    CreateOrUpdateHouse,
    CreateOrUpdateVoted,
    CreateOrUpdateBestMove,
    CreateOrUpdateDisqualified,
    CreateOrUpdateSheriffChecks,
    CreateOrUpdateSheriffVersion,
    CreateOrUpdateNominatedForBest
)
from zlo.domain.handlers import (
    CreateOrUpdateGameHandler,
    CreateOrUpdateVotedHandler,
    CreateOrUpdateHouseHandler,
    CreateOrUpdateBestMoveHandler,
    CreateOrUpdateDisqualifiedHandler,
    CreateOrUpdateSheriffVersionHandler,
    CreateOrUpdateNominatedForBestHandler,
    CreateOrUpdateBestMoveHandler,
    CreateOrUpdateDisqualifiedHandler,
    CreateOrUpdateSheriffChecksHandler,
    CreateOrUpdateSheriffVersionHandler,
    CreateOrUpdateNominatedForBestHandler,
)


def map_handlers(bus: MessageBus):
    bus.register(CreateOrUpdateGame, CreateOrUpdateGameHandler)
    bus.register(CreateOrUpdateVoted, CreateOrUpdateVotedHandler)
    bus.register(CreateOrUpdateHouse, CreateOrUpdateHouseHandler)
    bus.register(CreateOrUpdateBestMove, CreateOrUpdateBestMoveHundler)
    bus.register(CreateOrUpdateDisqualified, CreateOrUpdateDisqualifiedHandler)
    bus.register(CreateOrUpdateSheriffVersion, CreateOrUpdateSheriffVersionHundler)
    bus.register(CreateOrUpdateNominatedForBest, CreateOrUpdateNominatedForBestHundler)
    bus.register(CreateOrUpdateBestMove, CreateOrUpdateBestMoveHandler)
    bus.register(CreateOrUpdateDisqualified, CreateOrUpdateDisqualifiedHandler)
    bus.register(CreateOrUpdateSheriffChecks, CreateOrUpdateSheriffChecksHandler)
    bus.register(CreateOrUpdateSheriffVersion, CreateOrUpdateSheriffVersionHandler)
    bus.register(CreateOrUpdateNominatedForBest, CreateOrUpdateNominatedForBestHandler)
