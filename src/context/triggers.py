from context.network import NetworkContext


class Triggers:
    def __init__(self, triggers, network_context: NetworkContext):
        self.triggers = {}
        self.network_context = network_context
        self.add_multiple_triggers(triggers)

    def add_multiple_triggers(self, triggers):
        for trigger in triggers:
            added = False
            index = 0
            while not added:
                if not self.triggers.get(index):
                    trigger["index"] = index
                    self.triggers[index] = trigger
                    added = True
                else:
                    index += 1

        self.network_context.add_triggers(triggers)

        return triggers

    def add_trigger(self, trigger):
        triggers = self.add_multiple_triggers([trigger])
        return triggers[0]["index"]

    def del_multiple_triggers(self, indexes):
        deleted_indexes = []
        for index in indexes:
            deleted = self.triggers.pop(index, None)
            if deleted:
                deleted_indexes.append(index)

        self.network_context.del_triggers(deleted_indexes)

        return deleted_indexes

    def del_trigger(self, index):
        deleted_indexes = self.del_multiple_triggers([index])

        if len(deleted_indexes) > 0:
            return deleted_indexes[0]
        else:
            return -1
