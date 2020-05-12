import commands
import argparse

def parse_input():
    # Parser contenitore 
    parser = argparse.ArgumentParser()

    # Subparser
    subparser = parser.add_subparsers(help="commands", dest='command')

    # Trivector
    trivector_parser = subparser.add_parser('trivector')
    trivector_parser.add_argument('id_vent', type=str, help='Bocca')
    trivector_parser.add_argument('-t', '--threshold', type=float, default=0.001, help="Soglia")
    trivector_parser.add_argument('-neigh', '--neighborhood', type=str, choices=['moore', 'neumann'], default=None, help='Vicinato')
    trivector_parser.add_argument('-r', '--radius', type=int, default=1, help="Raggio del vicinato")

    # Autocut
    autocut_parser = subparser.add_parser('autocut')
    autocut_parser.add_argument('id_vent', type=str, help='Bocca')
    autocut_parser.add_argument('-t', '--threshold', type=float, default=0.001, help="Soglia del trivector")
    autocut_parser.add_argument('-neigh', '--neighborhood', type=str, choices=['moore', 'neumann'], default=None, help='Vicinato')
    autocut_parser.add_argument('-r', '--radius', type=int, default=1, help="Raggio del vicinato")
    autocut_parser.add_argument('-dist', '--distance', type=int, default=4, help="Distanza dalla bocca")
    autocut_parser.add_argument('-dim', '--dimension', type=int, default=2, help="Numero archi da tagliare")
    autocut_parser.add_argument('-mod', '--mode', type=str, choices=['iterative', 'batch'], default='iterative', help='Metodo di taglio archi')
    autocut_parser.add_argument('-me', '--measure', type=str, choices=['trasmittance', 'weight'], default='trasmittance', help='Misura da utilizzare per il taglio')
    
    return parser.parse_args()


def switch_command(args):
    if args.command == "trivector":
        commands.trivector_cmd(args.id_vent, args.neighborhood, args.radius, args.threshold)
    elif args.command == "autocut":
        commands.auto_cut_edges(args.id_vent, args.distance, args.neighborhood, args.dimension, args.mode, args.measure, args.radius)

args = parse_input()
switch_command(args)