# ################### Movetables describe the transformation of the coordinates by cube moves. #########################

from os import path
import array as ar
import solver2x2x2.cubie as cb
import solver2x2x2.enums as enums
from solver2x2x2.defs import N_TWIST, N_CORNERS, N_MOVE

folder = 'solver2x2x2'
a = cb.CubieCube()
# ############################ Move table for the the corners. ##################################

# The twist coordinate describes the 3^6 = 729 possible orientations of the 8 corners
fname = "move_corntwist"
if not path.isfile(path.join(folder, fname)):
    print("creating " + fname + " table...")
    corntwist_move = ar.array('H', [0 for i in range(N_TWIST * N_MOVE)])
    for i in range(N_TWIST):
        a.set_cornertwist(i)
        for j in (enums.Color.U, enums.Color.R, enums.Color.F):  # three faces U, R, F
            for k in range(3):  # three moves for each face, for example U, U2, U3 = U'
                a.multiply(cb.basicMoveCube[j])
                corntwist_move[N_MOVE * i + 3 * j + k] = a.get_corntwist()
            a.multiply(cb.basicMoveCube[j])  # 4. move restores face
    fh = open(path.join(folder, fname), "wb")
    corntwist_move.tofile(fh)
    fh.close()
    print("loading " + fname + " table...")
    print()
else:
    print("loading " + fname + " table...")
    fh = open(path.join(folder, fname), "rb")
    corntwist_move = ar.array('H')
    corntwist_move.fromfile(fh, N_TWIST * N_MOVE)
fh.close()





# The corners coordinate describes the 7! = 5040 permutations of the corners.
fname = "move_cornperm"
if not path.isfile(path.join(folder, fname)):
    print("creating " + fname + " table...")
    cornperm_move = ar.array('H', [0 for i in range(N_CORNERS * N_MOVE)])
    # Move table for the corners. corner  < 40320
    for i in range(N_CORNERS):
        if (i+1) % 200 == 0:
            print('.', end='', flush=True)
        a.set_corners(i)
        for j in (enums.Color.U, enums.Color.R, enums.Color.F):  # three faces U, R, F
            for k in range(3):
                a.multiply(cb.basicMoveCube[j])
                cornperm_move[N_MOVE * i + 3 * j + k] = a.get_cornperm()
            a.multiply(cb.basicMoveCube[j])
    fh = open(path.join(folder, fname), "wb")
    cornperm_move.tofile(fh)
    fh.close()
    print("\nloading " + fname + " table...")
    print()
else:
    print("loading " + fname + " table...")
    fh = open(path.join(folder, fname), "rb")
    cornperm_move = ar.array('H')
    cornperm_move.fromfile(fh, N_CORNERS * N_MOVE)
fh.close()
########################################################################################################################
