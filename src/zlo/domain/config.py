from zlo.adapters.infrastructure import MessageBus
from zlo.domain.events import (
    CreateOrUpdateGame,
    CreateOrUpdateHouse,
    CreateOrUpdateVoted,
    CreateOrUpdateBestMove,
    CreateOrUpdateDisqualified,
    CreateOrUpdateSheriffVersion,
    CreateOrUpdateNominatedForBest
)
from zlo.domain.handlers import (
    CreateOrUpdateGameHandler,
    CreateOrUpdateVotedHundler,
    CreateOrUpdateHouseHandler,
    CreateOrUpdateBestMoveHundler,
    CreateOrUpdateDisqualifiedHundler,
    CreateOrUpdateSheriffVersionHundler,
    CreateOrUpdateNominatedForBestHundler,
)


def map_handlers(bus: MessageBus):
    bus.register(CreateOrUpdateGame, CreateOrUpdateGameHandler)
    bus.register(CreateOrUpdateVoted, CreateOrUpdateVotedHundler)
    bus.register(CreateOrUpdateHouse, CreateOrUpdateHouseHandler)
    bus.register(CreateOrUpdateBestMove, CreateOrUpdateBestMoveHundler)
    bus.register(CreateOrUpdateDisqualified, CreateOrUpdateDisqualifiedHundler)
    bus.register(CreateOrUpdateSheriffVersion, CreateOrUpdateSheriffVersionHundler)
    bus.register(CreateOrUpdateNominatedForBest, CreateOrUpdateNominatedForBestHundler)
