import commands
import argparse

def parse_input():
    # Parser contenitore 
    parser = argparse.ArgumentParser()

    # Subparser
    subparser = parser.add_subparsers(help="commands", dest='command')

    # Trivector
    trivector_parser = subparser.add_parser('trivector')
    trivector_parser.add_argument('id_vent', type=str, help='ID of grid Vent')
    trivector_parser.add_argument('-t', '--threshold', type=float, default=0.001, help="Trivector threshold. Default=0.001")
    trivector_parser.add_argument('-neigh', '--neighborhood', type=str, choices=['moore', 'neumann'], default=None, help='Neighborhood of Vent. Default=None')
    trivector_parser.add_argument('-r', '--radius', type=int, default=1, help="Radius of the neighborhood. Default=1")

    # Autocut
    autocut_parser = subparser.add_parser('autocut')
    autocut_parser.add_argument('id_vent', type=str, help='Bocca')
    autocut_parser.add_argument('-t', '--threshold', type=float, default=0.001, help="Trivector threshold. Default=0.001")
    autocut_parser.add_argument('-neigh', '--neighborhood', type=str, choices=['moore', 'neumann'], default=None, help='Neighborhood of Vent. Default=None')
    autocut_parser.add_argument('-r', '--radius', type=int, default=1, help="Radius of the neighborhood. Default=1")
    autocut_parser.add_argument('-dist', '--distance', type=int, default=4, help="Minimum distance from Vent. Default=4")
    autocut_parser.add_argument('-dim', '--dimension', type=int, default=2, help="Number of edges to cut. Default=2")
    autocut_parser.add_argument('-mod', '--mode', type=str, choices=['iterative', 'batch'], default='iterative', help='Method for cutting. Default=iterative')
    autocut_parser.add_argument('-me', '--measure', type=str, choices=['trasmittance', 'weight'], default='trasmittance', help='Measure for cutting. Default=trasmittance')
    
    return parser.parse_args()


def switch_command(args):
    if args.command == "trivector":
        commands.trivector_cmd(args.id_vent, args.neighborhood, args.radius, args.threshold)
    elif args.command == "autocut":
        commands.auto_cut_edges(args.id_vent, args.distance, args.neighborhood, args.dimension, args.mode, args.measure, args.radius)

args = parse_input()
switch_command(args)