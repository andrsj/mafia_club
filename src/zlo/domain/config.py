from zlo.adapters.infrastructure import MessageBus
from zlo.domain.events import (
    CreateOrUpdateGame,
    CreateOrUpdateHouse,
    CreateOrUpdateVoted,
    CreateOrUpdateKills,
    CreateOrUpdateMisses,
    CreateOrUpdateBestMove,
    CreateOrUpdateDonChecks,
    CreateOrUpdateHandOfMafia,
    CreateOrUpdateDisqualified,
    CreateOrUpdateSheriffChecks,
    CreateOrUpdateBonusTolerant,
    CreateOrUpdateSheriffVersion,
    CreateOrUpdateBonusFromPlayers,
    CreateOrUpdateNominatedForBest,
)
from zlo.domain.handlers import (
    CreateOrUpdateGameHandler,
    CreateOrUpdateVotedHandler,
    CreateOrUpdateHouseHandler,
    CreateOrUpdateKillsHandler,
    CreateOrUpdateMissesHandler,
    CreateOrUpdateBestMoveHandler,
    CreateOrUpdateDonChecksHandler,
    CreateOrUpdateHandOfMafiaHandler,
    CreateOrUpdateDisqualifiedHandler,
    CreateOrUpdateBonusTolerantHandler,
    CreateOrUpdateSheriffChecksHandler,
    CreateOrUpdateSheriffVersionHandler,
    CreateOrUpdateBonusFromPlayersHandler,
    CreateOrUpdateNominatedForBestHandler,
)


def map_handlers(bus: MessageBus):
    bus.register(CreateOrUpdateGame, CreateOrUpdateGameHandler)
    bus.register(CreateOrUpdateVoted, CreateOrUpdateVotedHandler)
    bus.register(CreateOrUpdateHouse, CreateOrUpdateHouseHandler)
    bus.register(CreateOrUpdateKills, CreateOrUpdateKillsHandler)
    bus.register(CreateOrUpdateMisses, CreateOrUpdateMissesHandler)
    bus.register(CreateOrUpdateBestMove, CreateOrUpdateBestMoveHandler)
    bus.register(CreateOrUpdateDonChecks, CreateOrUpdateDonChecksHandler)
    bus.register(CreateOrUpdateHandOfMafia, CreateOrUpdateHandOfMafiaHandler)
    bus.register(CreateOrUpdateDisqualified, CreateOrUpdateDisqualifiedHandler)
    bus.register(CreateOrUpdateBonusTolerant, CreateOrUpdateBonusTolerantHandler)
    bus.register(CreateOrUpdateSheriffChecks, CreateOrUpdateSheriffChecksHandler)
    bus.register(CreateOrUpdateSheriffVersion, CreateOrUpdateSheriffVersionHandler)
    bus.register(CreateOrUpdateBonusFromPlayers, CreateOrUpdateBonusFromPlayersHandler)
    bus.register(CreateOrUpdateNominatedForBest, CreateOrUpdateNominatedForBestHandler)
