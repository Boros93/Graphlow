import commands
import sys, getopt

def switch_command(cmd):
    if cmd[0] == "trivector":
        commands.trivector_cmd(*cmd[1:])
    elif cmd[0] == "eruption":
        commands.eruption_cmd(*cmd[1:])
    elif cmd[0] == "montecarlo":
        commands.montecarlo_cmd(*cmd[1:])
    elif cmd[0] == "showsim":
        commands.show_sim(*cmd[1:])
    elif cmd[0] == "man":
        commands.man()
    elif cmd[0] == "exit":
        print("Goodbye!")
        return 0
    elif cmd[0] == "test": # comando per testare metodi
        commands.test(*cmd[1:])
    elif cmd[0] == "nodefromvent":
        commands.node_from_idvent(*cmd[1:])
    elif cmd[0] == "compare": # aggiunta di -w to a file
            commands.compare(*cmd[1:])
    else:
        print("Insert a valid command.")

_, cmd = getopt.getopt(sys.argv, "m", ["compare"])
if len(cmd) > 1:
    cmd = cmd[1:]
    switch_command(cmd)
else:
    print("========= Welcome in GRAPHLOW ==========")
    print(r"""\                   ooO
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
        state = switch_command(cmd)
        if state == 0:
            break