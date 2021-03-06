from starfish.pipeline.pipelinecomponent import PipelineComponent
from starfish.util.argparse import FsExistsType
from . import fourier_shift
from ._base import RegistrationAlgorithmBase


class Registration(PipelineComponent):
    @classmethod
    def implementing_algorithms(cls):
        return RegistrationAlgorithmBase.__subclasses__()

    @classmethod
    def add_to_parser(cls, subparsers):
        """Adds the registration component to the CLI argument parser."""
        register_group = subparsers.add_parser("register")
        register_group.add_argument("-i", "--input", type=FsExistsType(), required=True)
        register_group.add_argument("-o", "--output", type=FsExistsType(), required=True)
        register_group.set_defaults(starfish_command=Registration._cli)
        registration_subparsers = register_group.add_subparsers(dest="registration_algorithm_class")

        for algorithm_cls in cls.algorithm_to_class_map().values():
            group_parser = registration_subparsers.add_parser(algorithm_cls.get_algorithm_name())
            group_parser.set_defaults(registration_algorithm_class=algorithm_cls)
            algorithm_cls.add_arguments(group_parser)

        cls.register_group = register_group

    @classmethod
    def _cli(cls, args, print_help=False):
        """Runs the registration component based on parsed arguments."""
        if args.registration_algorithm_class is None or print_help:
            cls.register_group.print_help()
            cls.register_group.exit(status=2)

        instance = args.registration_algorithm_class.from_cli_args(args)

        from starfish.io import Stack

        print('Registering ...')
        s = Stack()
        s.read(args.input)

        instance.register(s)

        s.write(args.output)


Registration._ensure_algorithms_setup()
