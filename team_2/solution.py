import numpy as np
import json
import cvxpy as cp
import os

team_no = 2 
step_cost=-5

R = np.zeros((100))
A2 = np.zeros((60, 100))
ALPHA = np.zeros((60))
X = cp.Variable(100)


# Setting 1 for terminal states
for i in range(12):
    A2[i][i]=1


# Npo step cost for the states where health=0 as the game finishes
for v in range( 12,100 ):
    R[v] = step_cost

# the starting state is defined to be the one with heatlh=100, arrows=3 and stamina =100, which is the state 60-1=59
ALPHA[59] = 1


# Building the matrix for SHOOT Action
for health in range(5):
    for stamina in range(1,3):
        for arrows in range(1,4):
            if(health!=0):
                column= ((health*22)-10)+(6*arrows)+(3*stamina)-4
                row_start=health * 12 + 3 * arrows + stamina
                row_arrowhit=(health - 1) * 12 + 3 * (arrows - 1) + stamina - 1
                row_arrowmiss=health * 12 + 3 * (arrows - 1) + stamina - 1
                A2[row_start][column]=1
                A2[row_arrowhit][column]=-0.5
                A2[row_arrowmiss][column]=-0.5

# Building the matrix for DODGE Action
for health in range(5):
    if(health!=0):
        column=health * 22 + 11
        row_start=health * 12 + 11
        row_reach1=health * 12 + 9
        row_reach2=health * 12 + 10
        A2[row_start][column]=1
        A2[row_reach1][column]=-0.2
        A2[row_reach2][column]=-0.8

for health in range(5):
    if(health!=0):
        column=health * 22 + 8
        row_start=health * 12 + 10
        row_reach=health * 12 + 9
        A2[row_start][column]=1
        A2[row_reach][column]=-1

for health in range(5):
        for arrows in range(3):
            # stamina ==100
            if(health!=0 and arrows==0):
                column=health * 22 -7
                row_start=health * 12 + 2
                row_reach1=health * 12 + 1
                row_reach2=health * 12 
                row_reach3=health * 12 + 4
                row_reach4=health * 12 + 3
                A2[row_start][column]=1
                A2[row_reach1][column]=-0.16
                A2[row_reach2][column]=-0.04
                A2[row_reach3][column]=-0.64
                A2[row_reach4][column]=-0.16
            elif(health!=0 and arrows>0):
                column=health * 22 -7 + 6 * arrows
                row_start=health * 12 + 3 * arrows + 2
                row_reach1=health * 12 + 3 * arrows + 1
                row_reach2=health * 12 + 3 * arrows
                row_reach3=health * 12 + 3 * (arrows + 1) + 1
                row_reach4=health * 12 + 3 * (arrows + 1)
                A2[row_start][column]=1
                A2[row_reach1][column]=-0.16
                A2[row_reach2][column]= -0.04
                A2[row_reach3][column]= -0.64
                A2[row_reach4][column]=-0.16 

            #  stamina == 50
            if(health!=0 and arrows==0):
                column=health * 22 - 10 + 1
                row_start=health * 12 + 3 * arrows + 1
                row_reach1=health * 12 + 3 * arrows
                row_reach2=health * 12 + 3 * (arrows + 1)
                A2[row_start][column]=1
                A2[row_reach1][column]=-0.2
                A2[row_reach2][column]= -0.8
            elif(health!=0 and arrows>0):
                column=health * 22 - 10 + 6 * arrows
                row_start=health * 12 + 3 * arrows + 1
                row_reach1=health * 12 + 3 * arrows
                row_reach2=health * 12 + 3 * (arrows + 1)
                A2[row_start][column]=1
                A2[row_reach1][column]=-0.2
                A2[row_reach2][column]= -0.8

# Building the matrix for RECHARGE Action
for health in range(5):
    for stamina in range(2):
        if(health!=0):
            column=health * 22 - 10 + 2 * stamina
            row_start=health * 12 + stamina
            row_reach=health * 12 + stamina + 1
            A2[row_start][column]=0.8
            A2[row_reach][column]=-0.8

for health in range(5):
    for stamina in range(2):
        for arrows in range(1,4):
            if(health!=0):
                column=health * 22 - 10 + 6 * arrows + 2 * stamina - 2
                row_start=health * 12 + 3 * arrows + stamina
                row_reach=health * 12 + 3 * arrows + stamina + 1
                A2[row_start][column]=0.8
                A2[row_reach][column]=-0.8

# Solving the LPP using module from cvxpy
alpha=ALPHA.T
linear_constraints = [X >= 0, A2 @ X == alpha]
objective_function = cp.Maximize( R @ X )
equation = cp.Problem( objective_function, linear_constraints )
equation.solve()


# Forming the Optimal policy
j=0
optimal_policy=[]
for i in range(12):
    optimal_policy.append("NOOP")
    j=j+1  
for i in range(12,60):     
    if(i%12==0):
        optimal_policy.append("RECHARGE")
        j=j+1

    elif(i%12==1):

        a=X.value[j]
        j=j+1
        b=X.value[j]
        j=j+1
        if(a>b):
            optimal_policy.append("DODGE")
        else:
            optimal_policy.append("RECHARGE")
    
    elif(i%12==2):
        optimal_policy.append("DODGE")
        j=j+1

    elif(i%3==0):
        optimal_policy.append("RECHARGE")
        j=j+1

    elif(i%3==1):
        a=X.value[j]
        j=j+1
        b=X.value[j]
        j=j+1
        c=X.value[j]
        j=j+1
        if(a>b and a>c ):
            optimal_policy.append("SHOOT")
        elif(b>a and b>c ):
            optimal_policy.append("DODGE")
        else:
            optimal_policy.append("RECHARGE")
        
    elif(i%3==2):
        a=X.value[j]
        j=j+1
        b=X.value[j]
        j=j+1
        if(a>b):
            optimal_policy.append("SHOOT")
        else:
            optimal_policy.append("DODGE")


# Creating the dictionary 
dictionary=dict()
dictionary['a']=A2.tolist()
dictionary['r']=list(R)
opt_policy=[]
i_policy=0
for health in range(5):
    for arrows in range(4):
        for stamina in range(3):
            state=([health,arrows,stamina])
            state.append(optimal_policy[i_policy])
            opt_policy.append(state)
            i_policy=i_policy+1
dictionary['policy']=opt_policy
dictionary['x']=list(X.value)
dictionary['objective']=equation.value.tolist()
dictionary['alpha']=list(ALPHA)

# print(dictionary)

if(os.path.exists("./outputs")):
    open('./outputs/output.json', 'w').close()   
else:
    os.mkdir("./outputs")

with open('./outputs/output.json', 'w') as file:
    json.dump(dictionary,file)
