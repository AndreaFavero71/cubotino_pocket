# ###################### The solve function computes all optimal solving maneuvers #####################################
import solver2x2x2.face as face
import solver2x2x2.cubie as cubie
import solver2x2x2.coord as coord
import solver2x2x2.enums as en
import solver2x2x2.moves as mv
import solver2x2x2.pruning as pr
from solver2x2x2.defs import N_TWIST, QTM


solutions = []

def search(cornperm, corntwist, sofar, togo):
    
    global solutions
    # ##############################################################################################################
    if togo == 0:
        if len(solutions) == 0 or (len(solutions[-1]) == len(sofar)):
            solutions.append(sofar[:])
    
    else:
        for m in en.Move:  
            if QTM:
                if m in (en.Move.U2, en.Move.R2, en.Move.F2):
                    continue
                
                if len(sofar) > 0:
                    if (sofar[-1] // 3 == m // 3) and (sofar[-1] % 3 == 2 or m % 3 == 2):  # no x1 x3, x3 x1, x3 x3
                        continue
              
            else:
                if len(sofar) > 0:
                    if sofar[-1] // 3 == m //3: # successive moves on same face
                        continue

            cornperm_new = mv.cornperm_move[9 * cornperm + m]
            corntwist_new = mv.corntwist_move[9 * corntwist + m]

            if pr.corner_depth[N_TWIST * cornperm_new + corntwist_new] >= togo:
                continue  # impossible to reach solved cube in togo - 1 moves

            sofar.append(m)
            search(cornperm_new, corntwist_new, sofar, togo - 1)
            sofar.pop(-1)


def solve(cubestring):
    """Solves a 2x2x2 cube defined by its cube definition string.
     :param cubestring: The format of the string is given in the Facelet class defined in the file enums.py
     :return A list of all optimal solving maneuvers
    """
    global solutions
    fc = face.FaceCube()
    s = fc.from_string(cubestring) #####################################################################################
    if s is not True:
        return s  # Error in facelet cube
    cc = fc.to_cubie_cube()
    s = cc.verify()
    if s != cubie.CUBE_OK:
        return s  # Error in cubie cube

    solutions = []
    co_cube = coord.CoordCube(cc)
    togo = pr.corner_depth[N_TWIST * co_cube.cornperm + co_cube.corntwist]
    search(co_cube.cornperm, co_cube.corntwist, [], togo)
    
    compact = True   # compact=0 --> notations as per QTM, compact=1 --> notations as per FTM
    
    s = ''
    if not compact:
        for i in range(len(solutions)):  # use  range(min(len(solutions), 1)) if you want to return only a single solution
            ps = ''
            for m in solutions[i]:
                ps += m.name + ' '
            if QTM:
                ps += '(' + str(len(ps)//3) + 'q)\r\n'
            else:
                ps += '(' + str(len(ps)//3) + 'f)\r\n'
            s += ps
    
    else:
        for i in range(len(solutions)):  # use  range(min(len(solutions), 1)) if you want to return only a single solution
            ps = ''
            combo = 0
            q = 0
            l = len(solutions[i])
            for j, m in enumerate (solutions[i]):
                if combo:
                    ps += m.name[0] + '2 '
                    combo = 0
                    q += 2
                    continue
                if j<l-1:
                    if m == solutions[i][j+1]:
                        combo = 1
                        continue
                    else:
                        ps += m.name+' '
                        q += 1    
                else:
                    ps += m.name+' '
                    q += 1
            if QTM:
                ps += '(' + str(len(ps)//3) + 'q)\r\n'
            else:
                ps += '(' + str(len(ps)//3) + 'f)\r\n'
            s += ps
    
    return s
########################################################################################################################

