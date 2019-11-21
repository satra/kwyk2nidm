# kwyk2nidm
NIDMification of kwyk output

This project uses **kwyk** (https://github.com/neuronets/kwyk).
Paper, code, and model corresponding to [preprint](https://arxiv.org/abs/1812.01719), which is now published.

Cite: [McClure P, Rho N, Lee JA, Kaczmarzyk JR, Zheng CY, Ghosh SS, Nielson DM, Thomas AG, Bandettini P and Pereira F (2019) Knowing What You Know in Brain Segmentation Using Bayesian Deep Neural Networks. Front. Neuroinform. 13:67. doi:10.3389/fninf.2019.00067](https://www.frontiersin.org/articles/10.3389/fninf.2019.00067/full)

# Steps
## Run kwyk

## Interpret kwyk output for regional volumes
We include a BASH script, 'kwykput.sh' that takes a resulting output from kwyk, and used the FSL *fslstats* utility to determine the volume for each of the regions. This script uses the *kwyk_region_list.txt* file for the region lables (derived from *FreeSurfer*. It generates a text file (example provided *test_out.txt*) of the form:

<pre>
kwyk_index label number_voxels vol_inmm3
1 Cerebral-White-Matter 496396 496396.000000 
2 Ventricular-System 11025 11025.000000 
3 Cerebellum-White-Matter 32515 32515.000000 
4 Cerebellum-Cortex 144992 144992.000000 
5 Thalamus-Proper 18118 18118.000000 
6 Caudate 10851 10851.000000 
etc...
</pre>

## Convert the volume result file into NIDM
The steps for this include generating a kwykmap.json file that described 
the content of out reults file (*kwykmap.json*). As a developer, you can 
then work with ReproNim to create a set of custom terms for your software,
which are harmonized with other software. This generates a list of custom
data elements for the software with additional information. For example,
in the case of kwyk, this maps every structure to a common anatomical name,
measurement type, and measurement units.

```
kwyk:kwyk_000002 a kwyk:DataElement ;
    kwyk:label "Cerebral-White-Matter vol_inmm3 (mm^3)" ;
    kwyk:measure "vol_inmm3" ;
    kwyk:structure "Cerebral-White-Matter" ;
    kwyk:structure_id 1 ;
    kwyk:unit "mm^3" ;
    nidm:datumType ilx:0738276 ;
    nidm:hasUnit "mm^3" ;
    nidm:isAbout uberon:0002437 ;
    nidm:measureOf ilx:0112559 .
```

## Using the kwyk data elements to generate a NIDM result

### Software environment

You can run the kwyk2nidm script using either of the methods below.

1. Install `kwyk2nidm` into your Python 3 environment

```
pip install https://github.com/ReproNim/kwyk2nidm/archive/master.zip

kwyk2nidm -f kwyk_stats_file
```

2. Clone the repo and create a Docker container

```
git clone https://github.com/ReproNim/kwyk2nidm.git
cd kwyk2nidm
docker build -t kwyk2nidm:latest .
docker run -v $(pwd):/data kwyk2nidm -f /data/kwyk_stats_file
```

Running the kwyk2nidm command will generate an output file 
`kwyk_stats_file.ttl` unless a different name is specified using the 
`-o` flag.

To generate all the NIDM KWYK data elements add `-g` to the commands above. 
This will generate a `KWYK-NIDM.ttl` that should be added to provide the 
link between the NIDM stats file to the common data attributes.
 
# Great!  I have a NIDM **kwyk** result.  Now What???

1. Upload to ReproPond or ReproLake
2. Query across files!
3. Merge it with other NIDM, and query it!
