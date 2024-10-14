from typing import Dict, Tuple
from mpi4py import MPI
import numpy as np
from dataclasses import dataclass
import pandas as pd
import collections
import csv
import logging as pylog

from repast4py import core, random, space, schedule, logging, parameters
from repast4py import context as ctx
import repast4py
from repast4py.space import DiscretePoint as dpt
from datetime import datetime, timedelta

model = None

class Walker(core.Agent):

    TYPE = 0

    def __init__(self, local_id: int, rank: int, pt: dpt):
        super().__init__(id=local_id, type=Walker.TYPE, rank=rank)
        self.pt = pt

    def save(self) -> Tuple:
        """Saves the state of this Walker as a Tuple.

        Returns:
            The saved state of this Walker.
        """
        print('Saving the state...')
        return (self.uid, self.pt.coordinates)
    
    def walk(self, grid, model):

        print('Walking...')
        building_ids = list(model.dbuildings.keys())

        building_to_go = random.default_rng.choice(building_ids)
        pt = dpt(model.dbuildings[building_to_go]["pos"][0],
                     model.dbuildings[building_to_go]["pos"][1],
                     0)

        # --- Moving the agent trhough the grid
        self.pt = grid.move(self, pt)

walker_cache = {}

def restore_walker(walker_data: Tuple):
    """
    Args:
        walker_data: tuple containing the data returned by Walker.save.
    """
    print('Restoring walker data...')
    # uid is a 3 element tuple: 0 is id, 1 is type, 2 is rank
    uid = walker_data[0]
    pt_array = walker_data[1]
    pt = dpt(pt_array[0], pt_array[1], 0)

    if uid in walker_cache:
        walker = walker_cache[uid]
    else:
        walker = Walker(uid[0], uid[2], pt)
        walker_cache[uid] = walker

    walker.pt = pt
    return walker

class Model:
    """
    The Model class encapsulates the simulation, and is
    responsible for initialization (scheduling events, creating agents,
    and the grid the agents inhabit), and the overall iterating
    behavior of the model.

    Args:
        comm: the mpi communicator over which the model is distributed.
        params: the simulation input parameters
    """

    def __init__(self, comm: MPI.Intracomm, params: Dict):
        print('Init the model...')
        # create the schedule
        self.runner = schedule.init_schedule_runner(comm)
        self.runner.schedule_repeating_event(1, 1, self.step)
        self.runner.schedule_stop(params['stop.at'])
        #self.runner.schedule_end_event(self.at_end)

        # Load Params
        self.params = params

        coords = self.load_buildings()
        
        # create the context to hold the agents and manage cross process
        # synchronization
        self.context = ctx.SharedContext(comm)

        box = space.BoundingBox(coords[0], coords[1],
                                coords[2], coords[3], 0, 0)
        # create a SharedGrid of 'box' size with sticky borders that allows multiple agents
        # in each grid location.
        self.grid = space.SharedGrid(name='grid', bounds=box, borders=space.BorderType.Sticky,
                                     occupancy=space.OccupancyType.Multiple, buffer_size=2, comm=comm)
        self.context.add_projection(self.grid)
        
        rank = comm.Get_rank()
        rng = repast4py.random.default_rng
        
        building_ids = list(self.dbuildings.keys())
        
        for i in range(params['walker.count']):
            # get a random x,y location of a building in the grid
            building_to_go = random.default_rng.choice(building_ids)
            pt = dpt(self.dbuildings[building_to_go]["pos"][0],
                     self.dbuildings[building_to_go]["pos"][1],
                     0)
            # create and add the walker to the context
            walker = Walker(i, rank, pt)
            self.context.add(walker)
            self.grid.move(walker, pt)

        # Schedule
        #TODO: stick these into the params file.
        sim_start_str = '07/01/24 08:00:00'
        work_start_str = '09:00:00'
        work_end_str = '17:00:00'
        self.tick_duration = 5 # minutes

        self.sim_start = datetime.strptime(sim_start_str, '%m/%d/%y %H:%M:%S')
        self.work_start = datetime.strptime(work_start_str, '%H:%M:%S').time()
        self.work_end = datetime.strptime(work_end_str, '%H:%M:%S').time()
        self.current_time = self.sim_start        

    def step(self):
        print('Stepping...')
        self.current_time  = self.current_time + timedelta(minutes=self.tick_duration)
        if(self.current_time.time() == self.work_start):
            print('Time: ', self.current_time.time(), '  Going to work!')
            self.go_to_place()
        if(self.current_time.time() == self.work_end):
            print('Time: ', self.current_time.time(), '  Going home!')            
            print("Going home!")
            self.go_to_place()

        tick = self.runner.schedule.tick

        # TODO: It might be worth moving this into a python logger.  
        with open('./output/agent_log.csv', 'a', newline='') as agent_log:
            writer = csv.writer(agent_log, delimiter=',')
            for walker in self.context.agents():
                row=[tick, walker.id, walker.uid[2]]
                writer.writerow(row)

    def go_to_place(self):    
        print('Going...')    
        for walker in self.context.agents():
            walker.walk(self.grid, self)

        self.context.synchronize(restore_walker)        

    # creates buildings from file
    def load_buildings(self):
        print('Loading Building...')
        # --- Creating dictionary with buildings
        self.dbuildings = {}

        # --- Reading the input file
        # file_path = './input/input_buildings.csv'
        file_path = self.params.get('input_buildings')
        dframe = pd.read_csv(file_path)
        self.dbuildings = {dframe.iloc[i]['building_id']: 
                                {"type": int(dframe.iloc[i]['building_type']), 
                                    "pos" : np.array([dframe.iloc[i]['x_centroid'], dframe.iloc[i]['y_centroid']],
                                    dtype = int)} 
                            for i in dframe.T}
        coords = [int(dframe['x_centroid'].min()), int(dframe['x_centroid'].max())-int(dframe['x_centroid'].min()),
                  int(dframe['y_centroid'].min()), int(dframe['y_centroid'].max())-int(dframe['y_centroid'].min())]

        return  coords

    #def at_end(self):
        #self.data_set.close()

    def start(self):
        print('Starting...')
        self.runner.execute()

def run(params: Dict):
    # logging
    # TODO implement Python rotating logs using logging lib
    with open('./output/agent_log.csv', 'w', newline='') as agent_log:
        writer = csv.writer(agent_log, delimiter=',')
        row=['tick','agent_id', 'rank']
        writer.writerow(row)     
    model = Model(MPI.COMM_WORLD, params)
    model.start()
    print('FINISHED')

if __name__ == "__main__":

    pylog.basicConfig(level=pylog.DEBUG, format='%(relativeCreated)6d %(threadName)s %(message)s')
    parser = parameters.create_args_parser()
    args = parser.parse_args()
    params = parameters.init_params(args.parameters_file, args.parameters)
    run(params)
    print('MAIN FINISHED')
