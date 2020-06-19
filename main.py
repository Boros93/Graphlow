import commands
import argparse

def parse_input():
    # Parser contenitore 
    parser = argparse.ArgumentParser()

    # Subparser
    subparser = parser.add_subparsers(help="commands", dest='command')

    # Realsim
    realsim_parser = subparser.add_parser('realsim')
    realsim_parser.add_argument('id_vent', type=int, help='ID of grid Vent')
    realsim_parser.add_argument('-c', '--realclass', type=str, default="0", choices=['0','1','2','3','4','5','6'], help="Class of real simulation (0 for unified simulation). Default=0")
    realsim_parser.add_argument('-neigh', '--neighborhood', type=str, choices=['moore', 'neumann'], default=None, help='Neighborhood of Vent. Default=None')
    realsim_parser.add_argument('-r', '--radius', type=int, default=1, help="Radius of the neighborhood. Default=1")

    # Trivector
    trivector_parser = subparser.add_parser('trivector')
    trivector_parser.add_argument('id_vent', type=str, help='ID of grid Vent')
    trivector_parser.add_argument('-t', '--threshold', type=float, default=0.001, help="Trivector threshold. Default=0.001")
    trivector_parser.add_argument('-neigh', '--neighborhood', type=str, choices=['moore', 'neumann'], default=None, help='Neighborhood of Vent. Default=None')
    trivector_parser.add_argument('-r', '--radius', type=int, default=1, help="Radius of the neighborhood. Default=1")
    trivector_parser.add_argument('-g', '--graph', type=str, default="graphlow.gexf", help="Graph to use. Default=graphlow.gexf")

    # Eruption
    eruption_parser = subparser.add_parser('eruption')
    eruption_parser.add_argument('id_vent', type=str, help='ID of grid Vent')
    eruption_parser.add_argument('-d', '--days', type=int, default=7, help="Duration of eruption (in days). Default=7")
    eruption_parser.add_argument('-t', '--threshold', type=float, default=0.001, help="Eruption threshold. Default=0.001")
    eruption_parser.add_argument('-v', '--volume', type=float, default=1000, help="Eruption total volume. Default=1000")

    # Montecarlo
    montecarlo_parser = subparser.add_parser('montecarlo')
    montecarlo_parser.add_argument('id_vent', type=str, help='ID of grid Vent')
    montecarlo_parser.add_argument('-e', '--epochs', type=int, default=100, help="Number of Montecarlo's epochs. Default=100")
    montecarlo_parser.add_argument('-c', '--chance', type=float, default=0.0, help="Eruption threshold. Default=0.001")

    # Autocut
    autocut_parser = subparser.add_parser('autocut')
    autocut_parser.add_argument('id_vent', type=str, help='ID of grid Vent')
    autocut_parser.add_argument('-neigh', '--neighborhood', type=str, choices=['moore', 'neumann'], default=None, help='Neighborhood of Vent. Default=None')
    autocut_parser.add_argument('-r', '--radius', type=int, default=1, help="Radius of the neighborhood. Default=1")
    autocut_parser.add_argument('-dist', '--distance', type=int, default=4, help="Minimum distance from Vent. Default=4")
    autocut_parser.add_argument('-dim', '--dimension', type=int, default=2, help="Number of edges to cut. Default=2")
    autocut_parser.add_argument('-mod', '--mode', type=str, choices=['iterative', 'batch'], default='iterative', help='Method for cutting. Default=iterative')
    
    # Manual cut
    cut_parser = subparser.add_parser('cut')
    cut_parser.add_argument('id_vent', type=str, help='ID of grid Vent')
    cut_parser.add_argument('edges', type=str, nargs='+', help='List of edges to cut')
    cut_parser.add_argument('-neigh', '--neighborhood', type=str, choices=['moore', 'neumann'], default=None, help='Neighborhood of Vent. Default=None')
    cut_parser.add_argument('-r', '--radius', type=int, default=1, help="Radius of the neighborhood. Default=1") 

    # Immunological train
    imm_parser = subparser.add_parser('immunological')
    imm_parser.add_argument('id_vent', type=int, help='Initial vent')
    imm_parser.add_argument('-size', '--size', type=int, default=10, help='Dimension of area. Default=10')
    imm_parser.add_argument('-step', '--step', type=int, default=4, help='Distance between vents. Default=4')
    imm_parser.add_argument('-pop', '--population', type=int, default=5, help="Population size of the algorithm. Default=5")
    imm_parser.add_argument('-rho', '--rho', type=int, default=8, help='Mutation rate. Default=8')
    imm_parser.add_argument('-e', '--epochs', type=int, default=10, help='Number of epochs. Default=10')

    # Plot training result 2d
    plot2d_parser = subparser.add_parser('plot2d')
    plot2d_parser.add_argument('metric', type=str, choices=['precision', 'recall'], help="Metric to plot")
    plot2d_parser.add_argument('id_vent', type=int, help='Initial vent of the grid')
    plot2d_parser.add_argument('-size', '--size', type=int, default=10, help='Dimension of area. Default=10')
    plot2d_parser.add_argument('-step', '--step', type=int, default=4, help='Distance between vents. Default=4')

    # Plot training result 3d
    plot3d_parser = subparser.add_parser('plot3d')
    plot3d_parser.add_argument('metric', type=str, choices=['precision', 'recall'], help="Metric to plot")
    plot3d_parser.add_argument('id_vent', type=int, help='Initial vent of the grid')
    plot3d_parser.add_argument('-size', '--size', type=int, default=10, help='Dimension of area. Default=10')
    plot3d_parser.add_argument('-step', '--step', type=int, default=4, help='Distance between vents. Default=4')
    
    return parser.parse_args()


def switch_command(args):
    if args.command == "trivector":
        commands.trivector_cmd(id_vent=args.id_vent, neighbor_method=args.neighborhood, radius=args.radius, threshold=args.threshold, graph=args.graph)
    elif args.command == "eruption":
        commands.eruption_cmd(id_vent=args.id_vent, volume=args.volume, n_days=args.days, threshold=args.threshold)
    elif args.command == "montecarlo":
        commands.montecarlo_cmd(id_vent=args.id_vent, n_epochs=args.epochs, second_chance=args.chance)
    elif args.command == "autocut":
        commands.autocut_cmd(id_vent=args.id_vent, distance=args.distance, 
                                neighbor_method=args.neighborhood, dimension=args.dimension, mode=args.mode, radius=args.radius)
    elif args.command == "cut":
        commands.cut_cmd(id_vent=args.id_vent, list_edges=args.edges, neighbor_method=args.neighborhood, radius=args.radius)
    elif args.command == "realsim":
        commands.realsim_cmd(id_vent=args.id_vent, real_class=args.realclass, neighbor_method=args.neighborhood, radius=args.radius)
    elif args.command == "immunological":
        commands.immunological_train_cmd(id_vent=args.id_vent, size=args.size, step=args.step, population_len=args.population, rho=args.rho, epochs=args.epochs)
    elif args.command == "plot2d":
        commands.plot_2d_cmd(metric=args.metric, id_vent=args.id_vent, size=args.size, step=args.step)
    elif args.command == "plot3d":
        commands.plot_3d_cmd(metric=args.metric, id_vent=args.id_vent, size=args.size, step=args.step)
        
args = parse_input()
switch_command(args)