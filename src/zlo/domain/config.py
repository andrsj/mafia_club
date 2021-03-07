from zlo.adapters.infrastructure import MessageBus
from zlo.domain import events
from zlo.domain import handlers


DATA_FORMAT = "%d/%m/%Y"


def map_handlers(bus: MessageBus):
    bus.register(events.CreateOrUpdateGame, handlers.CreateOrUpdateGameHandler)
    bus.register(events.CreateOrUpdateVoted, handlers.CreateOrUpdateVotedHandler)
    bus.register(events.CreateOrUpdateHouse, handlers.CreateOrUpdateHouseHandler)
    bus.register(events.CreateOrUpdateKills, handlers.CreateOrUpdateKillsHandler)
    bus.register(events.CreateOrUpdateBreaks, handlers.CreateOrUpdateBreaksHandler)
    bus.register(events.CreateOrUpdateMisses, handlers.CreateOrUpdateMissesHandler)
    bus.register(events.CreateOrUpdateDevises, handlers.CreateOrUpdateDeviseHandler)
    bus.register(events.CreateOrUpdateBestMove, handlers.CreateOrUpdateBestMoveHandler)
    bus.register(events.CreateOrUpdateDonChecks, handlers.CreateOrUpdateDonChecksHandler)
    bus.register(events.CreateOrUpdateHandOfMafia, handlers.CreateOrUpdateHandOfMafiaHandler)
    bus.register(events.CreateOrUpdateDisqualified, handlers.CreateOrUpdateDisqualifiedHandler)
    bus.register(events.CreateOrUpdateBonusTolerant, handlers.CreateOrUpdateBonusTolerantHandler)
    bus.register(events.CreateOrUpdateSheriffChecks, handlers.CreateOrUpdateSheriffChecksHandler)
    bus.register(events.CreateOrUpdateBonusFromHeading, handlers.CreateOrUpdateBonusHeadingHandler)
    bus.register(events.CreateOrUpdateSheriffVersion, handlers.CreateOrUpdateSheriffVersionHandler)
    bus.register(events.CreateOrUpdateBonusFromPlayers, handlers.CreateOrUpdateBonusFromPlayersHandler)
    bus.register(events.CreateOrUpdateNominatedForBest, handlers.CreateOrUpdateNominatedForBestHandler)
