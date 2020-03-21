import commands
import sys

print("========= Welcome in GRAPHLOW ==========")
print(r"""\                  ooO
                     ooOOOo
                   oOOOOOOoooo
                 ooOOOooo  oooo
                /vvv\
               /V V V\ 
              /V  V  V\          
             /     V   \          AAAAH!  RUN FOR YOUR LIVES!
            /      VV   \               /
  ____     /        VVV  \   	  o          o
 /\      /        VVVV     \     /-   o     /-
/  \   /           VVVVVVV   \  /\  -/-    /\
                    VVVVVVVVVVVVV   /\
                    """)
while True:
    print(r"""Available commands: 
- man
- eruption [id_vent] [volume] [n_days] [alpha] [threshold]
- showsim [id_vent] [class]
- graph_to_matrix
- norm
- nodefromvent [id_vent]
- unify [id_vent] [d | c]
- exit""")
    cmd = input("Insert a command > ")
    cmd = cmd.split(" ")
    if cmd[0] == "eruption":
        commands.begin_eruption(*cmd[1:])
    elif cmd[0] == "showsim":
        commands.show_sim(*cmd[1:])
    elif cmd[0] == "man":
        commands.man()
    elif cmd[0] == "exit":
        print("Goodbye!")
        break
    elif cmd[0] == "test": # comando per testare metodi
        commands.test()
    elif cmd[0] == "norm": # normalizza 
        commands.norm_weight()
    elif cmd[0] == "unify": # unifica le simulazioni
        if cmd[2] == 'c' or cmd[2] == 'd':
            commands.unify(*cmd[1:])
        else:
            print("insert 'd' or 'c' after id_vent. 'd' = discrete, 'c' = continuous")
    elif cmd[0] == "nodefromvent":
        commands.node_from_idvent(*cmd[1:])
    elif cmd[0] == "proberuption":
        commands.prob_algorithm(*cmd[1:])
    else:
        print("Insert a valid command.")

