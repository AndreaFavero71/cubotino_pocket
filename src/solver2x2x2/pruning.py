# ##################### The pruning table cuts the search tree during the search. ######################################
# ########################## In this case it it gives the exact distance to the solved state. ##########################

import solver2x2x2.defs as defs
import solver2x2x2.enums as enums
import solver2x2x2.moves as mv
from os import path
import array as ar

corner_depth = None
folder = 'solver2x2x2'

def create_cornerprun_table():
    """Creates/loads the corner pruning table."""
    
    if defs.QTM:
        fname = "cornerprun_QTM"
    else:
        fname = "cornerprun"
    
    global corner_depth
    if not path.isfile(path.join(folder, fname)):
        print("creating " + fname + " table...")
        corner_depth = ar.array('b', [-1] * (defs.N_CORNERS * defs.N_TWIST))
        corners = 0  # values for solved cube
        twist = 0
        corner_depth[defs.N_TWIST * corners + twist] = 0
        done = 1
        depth = 0
        while done != defs.N_CORNERS * defs.N_TWIST:
            for corners in range(defs.N_CORNERS):
                for twist in range(defs.N_TWIST):
                    if corner_depth[defs.N_TWIST * corners + twist] == depth:
                        for m in enums.Move:
                            if defs.QTM:  # defines QTM or FTM
                                if m not in (enums.Move.U2, enums.Move.R2, enums.Move.F2):
                                    corners1 = mv.cornperm_move[9 * corners + m]
                                    twist1 = mv.corntwist_move[9 * twist + m]
                                    idx1 = defs.N_TWIST * corners1 + twist1
                                    if corner_depth[idx1] == -1:  # entry not yet filled
                                        corner_depth[idx1] = depth + 1
                                        done += 1
                                        if done % 50000 == 0:
                                            print('.', end='', flush=True)
                            
                            elif not defs.QTM:  # defines QTM or FTM
                                corners1 = mv.cornperm_move[9 * corners + m]
                                twist1 = mv.corntwist_move[9 * twist + m]
                                idx1 = defs.N_TWIST * corners1 + twist1
                                if corner_depth[idx1] == -1:  # entry not yet filled
                                    corner_depth[idx1] = depth + 1
                                    done += 1
                                    if done % 50000 == 0:
                                        print('.', end='', flush=True)
            depth += 1

        print("\nloading " + fname + " table...")
        print()
        fh = open(path.join(folder, fname), "wb")
        corner_depth.tofile(fh)
    else:
        print("loading " + fname + " table...")
        fh = open(path.join(folder, fname), "rb")
        corner_depth = ar.array('b')
        corner_depth.fromfile(fh, defs.N_CORNERS * defs.N_TWIST)
    fh.close()

create_cornerprun_table()


