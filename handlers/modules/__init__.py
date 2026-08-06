from . import (
    admin, warnings, locks, filters, notes, greetings, rules,
    antiflood, info, pin, purges, reports, karma, fun,
    approval, blocklists, disabling, stats, antichannel, misc, anime, broadcast
)

ALL_MODULES = [
    admin, warnings, locks, filters, notes, greetings, rules,
    antiflood, info, pin, purges, reports, karma, fun,
    approval, blocklists, disabling, stats, antichannel, misc, anime, broadcast,
]

def load_all_handlers(application):
    for module in ALL_MODULES:
        for handler in module.get_handlers():
            application.add_handler(handler)
