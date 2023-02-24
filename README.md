# NCTPtools

Tools to assist in the management of data for the Nebraska Crop Testing Program (NCTP)

### API Token:
Get the variety testing API token, create a config.json in the root of this project and add the field  `{ "api_token": "asdgjkbq34tidfgi4t..." }`

### Usage

```
$ python cli.py -h
usage: cli.py [-h] -e {local,prod} [-l] {payloads,upload} ...

options:
  -h, --help            show this help message and exit
  -e {local,prod}, --environment {local,prod}
                        Upload the data to the provided environment
  -l, --loud            How much to log about outgoing requests

actions:
  {payloads,upload}     Actions
    payloads            Generate request payloads
```

The top level command provides a set of options available for any subcommands. 

-e, --environment { local | prod }
- specifies the environment against which you'll be uploading data (local or prod). Neither local nor prod are behind CAS, dev and stage are so I didn't include them. If this proves to be the preferred method for uploading data, then fork the repo and make the necessary modifications.

-l, --loud
- spits out a bunch of info to the terminal

### Payloads Subcommand
```
$ python cli.py -e prod -l payloads -h
usage: cli.py payloads [-h] -i INPATH -o OUTPATH

options:
  -h, --help            show this help message and exit
  -i INPATH, --inpath INPATH
                        Path to trial csv data
  -o OUTPATH, --outpath OUTPATH
                        Where to output data
```

-i, --inpath {path-to-harvest-year-trials}
- specifies the input path which in the case of `payloads` is the trial directory for an entire harvest year i.e. trial_sites.csv, characteristics.csv and the results directories organized by site type (rainfed, irrigated, intensive_management, organic).

-o, --outpath {payloads-output}
- specifies the output directory, or where all the payloads will be dumped. This directory will be the input path to the upload command which will then submit those payloads to the server.

### Upload Subcommand
```
$ python cli.py -e prod upload -h
usage: cli.py upload [-h] -i INPATH [-y YEAR] [-r]
                     {all,sites,results,varieties} ...

positional arguments:
  {all,sites,results,varieties}

options:
  -h, --help            show this help message and exit
  -i INPATH, --inpath INPATH
                        Path to json payloads
  -y YEAR, --year YEAR  The harvest year for these payloads
  -r, --rewrite         Rewrite i.e. delete existing and write again
```

-i, --inpath {path-to-payloads}
- specifies the input path, which in this case is the output of the payloads command. 
-y, --year {4 dig year}
- specifies the harvest year these trials are for. Note that the harvest year publication id will be fetched from the environment you selected and may not apply to another environment. Make sure you're not re-using these payloads on another environment after you've submitted this one.
-r, --rewrite
- specifies that you wish to delete the records stored from a previous run and then re-submit them. This is useful in development if you realize you made a mistake with the data and want to ensure that records that were already added aren't duplicated on subsequent runs.


### Logging / Manifest

There will be a manifest generated in the payloads output directory when you run the upload command. This manaifest is useful for determining if there were any failed uploads so you can correct and re-run that data. Any successful uploads will respond with the newly created entity, and that entities primary key id will be stored in the payload file. This is how the --rewrite option knows what records to delete.


