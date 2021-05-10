import json
import argparse
from functools import partial
from app import settings
from app.database import utils
from app.database import models
from app.loader import (
    load_data,
    violation_row_to_instance,
    accident_row_to_instance,
    region_data_to_instances,
    country_town_data_to_instances,
    encrypt_uid_and_save_file
)
from app.transform import (
    patch_party_address_from_accident,
    patch_birthday_from_violation,
    patch_missing_violation,
    calculate_recidivist,
    calculate_age,
    encrypt_uid,
)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['init', 'describe', 'load', 'transform', 'encrypt'], default='describe',
                        help='Command line argument.')
    parser.add_argument('--db', choices=settings.DATABASES.keys(), default='default',
                        help='Database declared from settings.')
    parser.add_argument('--table', type=str, default=None, help='Table name.')
    parser.add_argument('--file', type=str, default=None, help='File path.')
    parser.add_argument('--sheet', type=int, default=0, help='Sheet No.')
    parser.add_argument('--output-dir', type=str, default=None, help='Output directory.')
    args = parser.parse_args()
    return args


def main():
    args = parse_arguments()
    if args.action == 'init':
        confirm_msg = (
            f"Do you want to drop tables in {args.db} database before recreate them? (y/n)"
        )
        drop = input(confirm_msg).lower() == "y"
        utils.init_database(args.db, drop)
        print('OK')
    if args.action == 'describe':
        if not args.table:
            raise argparse.ArgumentTypeError('Argument --table is missing.')
        result = utils.describe_table(args.table, args.db)
        json_result = json.dumps(result, indent=4, default=str)
        print(json_result)

    if args.action == 'load':
        for arg in ['table', 'file']:
            if not getattr(args, arg):
                raise argparse.ArgumentTypeError(f'Argument --{arg} is missing.')
        if args.table == 'violation':
            load_data(args.file, hook=violation_row_to_instance)
        elif args.table == 'accident':
            load_data(args.file, hook=accident_row_to_instance)
        elif args.table == 'country_town':
            load_data(args.file, hook=country_town_data_to_instances)
        elif args.table in ('divorce', 'old', 'indigenous', 'education', 'income_mid', 'income_avg'):
            mapping = {
                idx: year for idx, year in zip(range(4, 14), range(2010, 2021))
            }
            model_classes = {
                'divorce': models.Divorce,
                'old': models.Old,
                'indigenous': models.Indigenous,
                'education': models.Education,
                'income_mid': models.IncomeMid,
                'income_avg': models.IncomeAvg
            }
            load_data(args.file, sheet=args.sheet, hook=partial(
                region_data_to_instances, mapping=mapping, model_class=model_classes.get(args.table)
            ))
        else:
            raise argparse.ArgumentError(f'Unknown table {arg.table}.')

    if args.action == 'transform':
        # patch_birthday_from_violation()
        patch_party_address_from_accident()
        patch_missing_violation()
        calculate_recidivist()
        calculate_age()
        encrypt_uid()

    if args.action == 'encrypt':
        for arg in ['table', 'file', 'output_dir']:
            if not getattr(args, arg):
                raise argparse.ArgumentTypeError(f'Argument --{arg} is missing.')
        if args.table == 'violation':
            encrypt_uid_and_save_file(args.file, 3, args.output_dir)
        elif args.table == 'accident':
            encrypt_uid_and_save_file(args.file, 13, args.output_dir)


if __name__ == '__main__':
    main()
