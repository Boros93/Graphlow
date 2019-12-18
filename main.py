import commands
import sys

print("========= Welcome in SaveVolcanoPeople ==========")
print(r"""\                      ooO
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
    else:
        break

