from repast4py import core

class DeerAgent(core.Agent): 

    TYPE = 1

    def __init__(self, a_id, rank):
        super().__init__(id=a_id, type=DeerAgent.TYPE, rank=rank)

    def save(self):
        return (self.uid,)

    def step(self):
        grid = model.grid
        pt = grid.get_location(self)
        nghs = model.ngh_finder.find(pt.x, pt.y)  # include_origin=True)

        at = dpt(0, 0)
        maximum = [[], -(sys.maxsize - 1)]
        for ngh in nghs:
            at._reset_from_array(ngh)
            count = 0
            for obj in grid.get_agents(at):
                if obj.uid[1] == Human.TYPE:
                    count += 1
            if count > maximum[1]:
                maximum[0] = [ngh]
                maximum[1] = count
            elif count == maximum[1]:
                maximum[0].append(ngh)

        max_ngh = maximum[0][random.default_rng.integers(0, len(maximum[0]))]

        if not is_equal(max_ngh, pt.coordinates):
            direction = (max_ngh - pt.coordinates[0:3]) * 0.25
            cpt = model.space.get_location(self)
            # timer.start_timer('zombie_move')
            model.move(self, cpt.x + direction[0], cpt.y + direction[1])
            # timer.stop_timer('zombie_move')

        pt = grid.get_location(self)
        for obj in grid.get_agents(pt):
            if obj.uid[1] == Human.TYPE:
                obj.infect()
                break