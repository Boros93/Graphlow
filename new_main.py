import commands
import argparse

def parse_input():
    # Parser contenitore 
    parser = argparse.ArgumentParser()

    # Subparser
    subparser = parser.add_subparsers(help="commands", dest='command')

    # Realsim
    realsim_parser = subparser.add_parser('realsim')
    realsim_parser.add_argument('id_vent', type=str, help='ID of grid Vent')
    realsim_parser.add_argument('-c', '--realclass', type=str, default="0", choices=['0','1','2','3','4','5','6'], help="Class of real simulation (0 for unified simulation). Default=0")
    realsim_parser.add_argument('-neigh', '--neighborhood', type=str, choices=['moore', 'neumann'], default=None, help='Neighborhood of Vent. Default=None')
    realsim_parser.add_argument('-r', '--radius', type=int, default=1, help="Radius of the neighborhood. Default=1")

    # Trivector
    trivector_parser = subparser.add_parser('trivector')
    trivector_parser.add_argument('id_vent', type=str, help='ID of grid Vent')
    trivector_parser.add_argument('-t', '--threshold', type=float, default=0.001, help="Trivector threshold. Default=0.001")
    trivector_parser.add_argument('-neigh', '--neighborhood', type=str, choices=['moore', 'neumann'], default=None, help='Neighborhood of Vent. Default=None')
    trivector_parser.add_argument('-r', '--radius', type=int, default=1, help="Radius of the neighborhood. Default=1")

    # Autocut
    autocut_parser = subparser.add_parser('autocut')
    autocut_parser.add_argument('id_vent', type=str, help='ID of grid Vent')
    autocut_parser.add_argument('-neigh', '--neighborhood', type=str, choices=['moore', 'neumann'], default=None, help='Neighborhood of Vent. Default=None')
    autocut_parser.add_argument('-r', '--radius', type=int, default=1, help="Radius of the neighborhood. Default=1")
    autocut_parser.add_argument('-dist', '--distance', type=int, default=4, help="Minimum distance from Vent. Default=4")
    autocut_parser.add_argument('-dim', '--dimension', type=int, default=2, help="Number of edges to cut. Default=2")
    autocut_parser.add_argument('-mod', '--mode', type=str, choices=['iterative', 'batch'], default='iterative', help='Method for cutting. Default=iterative')
    autocut_parser.add_argument('-me', '--measure', type=str, choices=['trasmittance', 'weight'], default='trasmittance', help='Measure for cutting. Default=trasmittance')
    
    # Manual cut
    cut_parser = subparser.add_parser('cut')
    cut_parser.add_argument('id_vent', type=str, help='ID of grid Vent')
    cut_parser.add_argument('edges', type=str, nargs='+', help='List of edges to cut')
    cut_parser.add_argument('-neigh', '--neighborhood', type=str, choices=['moore', 'neumann'], default=None, help='Neighborhood of Vent. Default=None')
    cut_parser.add_argument('-r', '--radius', type=int, default=1, help="Radius of the neighborhood. Default=1") 
    
    return parser.parse_args()


def switch_command(args):
    if args.command == "trivector":
        commands.trivector_cmd(id_vent=args.id_vent, neighbor_method=args.neighborhood, radius=args.radius, threshold=args.threshold)
    elif args.command == "autocut":
        commands.autocut_cmd(id_vent=args.id_vent, distance=args.distance, 
                                neighbor_method=args.neighborhood, dimension=args.dimension, mode=args.mode, measure=args.measure, radius=args.radius)
    elif args.command == "cut":
        commands.cut_cmd(id_vent=args.id_vent, list_edges=args.edges, neighbor_method=args.neighborhood, radius=args.radius)
    elif args.command == "realsim":
        commands.realsim_cmd(id_vent=args.id_vent, real_class=args.realclass, neighbor_method=args.neighborhood, radius=args.radius)
        
args = parse_input()
switch_command(args)