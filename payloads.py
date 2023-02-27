from os import mkdir, listdir
from os.path import join, exists
import csv
import json
from http_client import *
from shutil import rmtree
import datetime as dt


SUMMARY_COLS = ["mean","lsd","cv","stderr","reps"]


def make_dir(path):
    if exists(path):
        rmtree(path)
    mkdir(path)


def sites_payloads(cli):
    sites_inpath = join(cli.args.inpath, "trial_sites.csv")
    sites_outpath = join(cli.args.outpath,'trial_sites')
    assert exists(sites_inpath)
    make_dir(sites_outpath)
    
    with open(sites_inpath, 'r') as file_obj:
        # print(f"{'irrigated':10}{'organic':10}{'intensive_management':20} = {'outcome':10}")
        for i,row in enumerate(csv.DictReader(file_obj)):
            if int(row['intensive_management']) == 1:
                site_type = 'intensive_management'
            elif int(row['organic']) == 1:
                site_type = 'organic'
            elif int(row['irrigated']) == 1:
                site_type = 'irrigated'
            else:
                site_type = 'rainfed'
            # print(f"{row['irrigated']:10}{row['organic']:10}{row['intensive_management']:20} = {site_type:10}")
            row["harvest_year_pub_id"] = None
            # replace with api call
            prefinal_outpath = join(sites_outpath, site_type)
            if not exists(prefinal_outpath):
                mkdir(prefinal_outpath)
            final_outpath = join(prefinal_outpath, f"{row['fips']}.json")
            j=1
            while exists(final_outpath):
                final_outpath = join(prefinal_outpath, f"{row['fips']}_{j}.json")
                j += 1

            with open(final_outpath, 'w') as outfile:
                json.dump(row, outfile)


def variety_payloads(cli):
    variety_path = join(cli.args.inpath, "characteristics.csv")
    varieties_outpath = join(cli.args.outpath, "varieties")
    make_dir(varieties_outpath)
    file_obj = open(variety_path, 'r')
    for i,row in enumerate(csv.DictReader(file_obj)):
        # varieties[row['name']]
        row["published_at"] = str(dt.date.today())
        with open(join(varieties_outpath, f"{i}.json"), 'w') as outfile:
            json.dump(row, outfile)


def results_payloads(cli):
    results_base_outpath = join(cli.args.outpath, "results")
    sites_outpath = join(cli.args.outpath,'trial_sites')
    make_dir(results_base_outpath)
    for site_type in ['irrigated', 'rainfed', 'intensive_management']:
        results_outpath = join(results_base_outpath, site_type)
        results_base_inpath = join(cli.args.inpath, site_type)
        mkdir(results_outpath)
        for fips_csv in listdir(results_base_inpath):
            inpath = join(results_base_inpath, fips_csv)
            fips_outpath = join(results_outpath, fips_csv[:5])
            mkdir(fips_outpath)
            sites_json_path = join(sites_outpath, site_type, f"{fips_csv[:5]}.json")
            if not exists(sites_json_path):
                print(f"Skipping results because site doesn't exist: {inpath}")
                continue
            with open(sites_json_path, 'r') as sites_json:
                sites_json = json.load(sites_json)
            with open(inpath, 'r') as file_obj:
                for i,row in enumerate(csv.DictReader(file_obj)):
                    row['trial_site_id'] = None
                    row['variety_id'] = None
                    del(row['variety_name'])
                    if row['name'] in SUMMARY_COLS:
                        for col in ['grain_yield','bushel_weight','plant_height','protein','kernel_weight']:
                            field_name = f"{row['name']}_{col}"
                            sites_json[field_name] = row[col]
                    else:   
                        final_outpath = join(fips_outpath, f"{i}.json")
                        j = 1
                        while exists(final_outpath):
                            final_outpath = join(fips_outpath, "f{i}_{j}.json")
                            j += 1
                        with open(final_outpath, 'w') as outfile:
                            json.dump(row, outfile)
                with open(sites_json_path, 'w') as site_json_file:
                    json.dump(sites_json, site_json_file)


def all_payloads(cli):
    make_dir(cli.args.outpath)
    sites_payloads(cli)
    variety_payloads(cli)
    results_payloads(cli)

    