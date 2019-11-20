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
The steps for this include generating a kwykmap.json file that described the content of out reults file (*kwykmap.json*). 

Install `kwyk2nidm` and call `kwyk2nidm -f kwyk_stats_file`
 
# Great!  I have a NIDM **kwyk** result.  Now What???
## Query it!

## Merge it with other NIDM, and query it!
