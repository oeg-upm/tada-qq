
class PMap:

    def __init__(self):
        self.mappings = dict()

    def add(self, props):
        found = False
        for p in props:
            if p in self.mappings:
                found = self.mappings[p]
                break
        if found is False:
            found = props[0]
            self.mappings[found] = found

        for p in props:
            self.mappings[p] = found

    def get(self, prop):
        if prop not in self.mappings:
            print(self.mappings)
            raise Exception("The provided property <%s> was not added." % prop)
        return self.mappings[prop]