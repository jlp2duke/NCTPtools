import argparse
import pathlib
from http_client import * 
from upload import all, sites, varieties, results
from payloads import all_payloads
from os.path import join, exists
from os import remove


class UploadAction(argparse.Action):
    
    env_domain_mappings = {
        "local":   "http://127.0.0.1:8000/api",
        "prod":    "https://varietytesting.unl.edu/api",
        "develop": "https://varietytesting-dev.unl.edu/api",
        "staging": "https://varietytesting-stage.unl.edu/api"
    }

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, 'domain', self.env_domain_mappings.get(values[0]))

    @staticmethod
    def arg_config():
        return {
            "help": "Upload the data to the provided environment",
            "nargs": 1,
            "choices": UploadAction.env_domain_mappings.keys(),
            "action": UploadAction,
            "default": "local"
        }


class Cli:

    def __init__(self):
        self.__parser = self.__define_parser()
        self.args = self.__parser.parse_args()
        self.__load_config()
        if hasattr(self.args, 'upload'):
            self.client = VarietyTestingHttpClient(self.args.domain,self.config,self.args.loud)
            self.__fetch_year()
            self.__open_and_set_manifest()

    def run(self):
        self.args.op(self)

    def write_to_manifest(self, why, path, *args):
        args_str = ',' + ','.join(map(lambda arg: str(arg).replace(",", "\\,"), args))
        self.manifest.write(f"[{why}],{path}{args_str}\n")

    def __load_config(self):
        with open('config.json', 'r') as config_file:
            self.config = json.load(config_file)

    def __fetch_year(self):
        year_id = self.client.get_year_id(self.args.year)        
        if year_id is None:
            print(f"\n> Have you created the harvest year publication?")
            exit("\nfailed\n")
        setattr(self.args, 'year_id', year_id)

    def __open_and_set_manifest(self):
        if exists(path:=join(self.args.inpath, 'manifest.csv')):
            remove(path)
        self.manifest = open(path, 'w')

    def __del__(self):
        if hasattr(self, 'manifest'):
            self.manifest.close()

    @staticmethod
    def __define_parser() -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser()
        
        parser.add_argument("-e", "--environment",  **UploadAction.arg_config(), required=True)
        parser.add_argument("-l", "--loud", help="How much to log about outgoing requests", action='store_true')
        command_subparsers = parser.add_subparsers(title = 'actions', help="Actions")

        payloads_parser = command_subparsers.add_parser('payloads', help='Generate request payloads')
        payloads_parser.add_argument("-i", "--inpath", help="Path to trial csv data", type=pathlib.Path, required=True)
        payloads_parser.add_argument("-o", "--outpath", default="./json", help="Where to output data", type=pathlib.Path, required=True)
        payloads_parser.set_defaults(op=all_payloads)

        upload_parser = command_subparsers.add_parser('upload', help='Upload data to a variety testing environment')
        upload_parser.set_defaults(upload=True)
        upload_parser.add_argument("-i", "--inpath", help="Path to json payloads", type=pathlib.Path, required=True)
        upload_parser.add_argument('-y', '--year', help="The harvest year for these payloads", type=int)
        upload_parser.add_argument('-r', '--rewrite', help="Rewrite i.e. delete existing and write again", action='store_true')

        upload_types = upload_parser.add_subparsers()

        all_upload_parser = upload_types.add_parser('all')
        all_upload_parser.set_defaults(op=all)
        
        site_upload_parser = upload_types.add_parser('sites')
        site_upload_parser.set_defaults(op=sites)
        
        results_parser = upload_types.add_parser('results')
        results_parser.set_defaults(op=results)
        
        varieties_parser = upload_types.add_parser('varieties')
        varieties_parser.set_defaults(op=varieties)

        return parser


cli = Cli()
cli.run()

