#!/usr/bin/env python
"""Utilities for extracting information from freesurfer stats files

"""

import json
import os
from collections import namedtuple
from pathlib import Path
import rdflib as rl
import pandas as pd

from . import __version__ as version

KWYK = namedtuple("KWYK", ["structure", "measure", "unit"])
cde_file = Path(os.path.dirname(__file__)) / "mapping_data" / "kwyk-cdes.json"
map_file = Path(os.path.dirname(__file__)) / "mapping_data" / "kwykmap.json"
KWYKNS = rl.Namespace("http://purl.org/nidash/kwyk#")


def read_kwyk_stats(kwyk_stats_file, force_error=True):
    """
    Reads a kwyk stats file
    :param kwyk_stats_file: path to kwyk stats file
    :return: measures
    """

    # open stats file, brain vols file as pandas dataframes
    kwyk_stats = pd.read_table(kwyk_stats_file, delimiter=" ", index_col=False)

    with open(cde_file, "r") as fp:
        kwyk_cde = json.load(fp)

    measures = []
    changed = False
    # iterate over columns in brain vols
    for row in kwyk_stats.iterrows():
        key_tuple_vox = KWYK(
            structure=row[1].label, measure="number_voxels", unit="voxels"
        )
        if str(key_tuple_vox) not in kwyk_cde:
            kwyk_cde["count"] += 1
            kwyk_cde[str(key_tuple_vox)] = {
                "id": f"{kwyk_cde['count']:0>6d}",
                "structure_id": row[1].kwyk_index,
                "label": f"{key_tuple_vox.structure} {key_tuple_vox.measure} ({key_tuple_vox.unit})",
            }
            if force_error:
                raise ValueError(
                    f"Key {key_tuple_vox} not found in KWYK data elements file"
                )
            changed = True
        measures.append(
            (f'{kwyk_cde[str(key_tuple_vox)]["id"]}', str(row[1].number_voxels))
        )
        key_tuple_vol = KWYK(structure=row[1].label, measure="vol_inmm3", unit="mm^3")
        if str(key_tuple_vol) not in kwyk_cde:
            kwyk_cde["count"] += 1
            kwyk_cde[str(key_tuple_vol)] = {
                "id": f"{kwyk_cde['count']:0>6d}",
                "structure_id": row[1].kwyk_index,
                "label": f"{key_tuple_vol.structure} {key_tuple_vol.measure} ({key_tuple_vol.unit})",
            }
            if force_error:
                raise ValueError(
                    f"Key {key_tuple_vol} not found in KWYK data elements file"
                )
            changed = True
        measures.append(
            (f'{kwyk_cde[str(key_tuple_vol)]["id"]}', str(row[1].vol_inmm3))
        )

    if changed:
        with open(cde_file, "w") as fp:
            json.dump(kwyk_cde, fp, indent=2)

    return measures


def create_kwyk_mapper():
    """Create KWYK to ReproNim mapping information

    Combines or updates cde file from information in map file
    """

    with open(map_file, "r") as fp:
        kwyk_map = json.load(fp)

    with open(cde_file, "r") as fp:
        kwyk_cde = json.load(fp)

    s = kwyk_map["Structures"]
    m = kwyk_map["Measures"]
    for key in kwyk_cde:
        if key == "count":
            continue
        key_tuple = eval(key)
        sk = key_tuple.structure
        mk = key_tuple.measure
        if sk not in s:
            s[sk] = dict(isAbout=None, kwyk_index=kwyk_map[key_tuple].structure_id)
        if mk not in m:
            m[mk] = dict(measureOf=None, datumType=None, hasUnit=key_tuple.unit)

        if s[sk]["isAbout"] is not None and (
            "UNKNOWN" not in s[sk]["isAbout"] and "CUSTOM" not in s[sk]["isAbout"]
        ):
            kwyk_cde[key]["isAbout"] = s[sk]["isAbout"]

        if m[key_tuple.measure]["measureOf"] is not None:
            kwyk_cde[key].update(**m[key_tuple.measure])

    with open(map_file, "w") as fp:
        json.dump(kwyk_map, fp, sort_keys=True, indent=2)
        fp.write("\n")

    with open(cde_file, "w") as fp:
        json.dump(kwyk_cde, fp, indent=2)
        fp.write("\n")

    return kwyk_map, kwyk_cde


def create_cde_graph(restrict_to=None):
    """Create an RDFLIB graph with the KWYK CDEs

    Any CDE that has a mapping will be mapped
    """
    with open(cde_file, "r") as fp:
        kwyk_cde = json.load(fp)
    from nidm.core import Constants

    nidm = Constants.NIDM
    kwyk = KWYKNS

    g = rl.Graph()
    g.bind("kwyk", kwyk)
    g.bind("nidm", nidm)
    g.bind("uberon", "http://purl.obolibrary.org/obo/UBERON_")
    g.bind("ilx", "http://uri.interlex.org/base/ilx_")

    g.add((kwyk["DataElement"], rl.RDFS['subClassOf'], nidm['DataElement']))
    for key, value in kwyk_cde.items():
        if key == "count":
            continue
        if restrict_to is not None:
            if value["id"] not in restrict_to:
                continue
        for subkey, item in value.items():
            if subkey == "id":
                kwykid = "kwyk_" + item
                g.add((kwyk[kwykid], rl.RDF.type, kwyk["DataElement"]))
                continue
            if item is None or "unknown" in str(item):
                continue
            if subkey in ["isAbout", "datumType", "measureOf"]:
                g.add((kwyk[kwykid], nidm[subkey], rl.URIRef(item)))
            elif subkey in ["hasUnit"]:
                g.add((kwyk[kwykid], nidm[subkey], rl.Literal(item)))
            elif subkey in ["label"]:
                g.add((kwyk[kwykid], rl.RDFS['label'], rl.Literal(item)))
            else:
                if isinstance(item, rl.URIRef):
                    g.add((kwyk[kwykid], kwyk[subkey], item))
                else:
                    g.add((kwyk[kwykid], kwyk[subkey], rl.Literal(item)))
        key_tuple = eval(key)
        for subkey, item in key_tuple._asdict().items():
            if item is None:
                continue
            g.add((kwyk[kwykid], kwyk[subkey], rl.Literal(item)))
    return g


def convert_stats_to_nidm(stats):
    """Convert a stats record into a NIDM entity

    Returns the entity and the prov document
    """
    from nidm.core import Constants
    from nidm.experiment.Core import getUUID
    import prov

    kwyk = prov.model.Namespace("kwyk", str(KWYKNS))
    niiri = prov.model.Namespace("niiri", str(Constants.NIIRI))
    nidm = prov.model.Namespace("nidm", "http://purl.org/nidash/nidm#")
    doc = prov.model.ProvDocument()
    e = doc.entity(identifier=niiri[getUUID()])
    e.add_asserted_type(nidm["KWYKStatsCollection"])
    e.add_attributes(
        {
            kwyk["kwyk_" + val[0]]: prov.model.Literal(
                val[1],
                datatype=prov.model.XSD["float"]
                if "." in val[1]
                else prov.model.XSD["integer"],
            )
            for val in stats
        }
    )
    return e, doc


def main():
    import argparse

    parser = argparse.ArgumentParser(
        prog="kwyk2nidm",
        description=(
            "This program will load in the KWYK brain segmentation "
            "outputs, augment the KWYK anatomical region designations "
            "with common data element anatomical designations, and "
            "save the statistics + region designations out as NIDM "
            "serializations (i.e. TURTLE, JSON-LD RDF)"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-f",
        "--kwyk_stats",
        dest="stats_file",
        required=True,
        type=str,
        help="KWYK stats file",
    )
    parser.add_argument(
        "-g",
        "--gen-nidm",
        dest="generate",
        action="store_true",
        default=False,
        help="Generate KWYK CDE graph (KWYK-NIDM.ttl)",
    )
    parser.add_argument(
        "-o",
        "--outfile",
        dest="outfile",
        type=str,
        help="Output name for KWYK NIDM file",
    )
    args = parser.parse_args()
    stats = read_kwyk_stats(args.stats_file)
    e, doc = convert_stats_to_nidm(stats)
    from nidm.core import Constants
    from nidm.experiment.Core import getUUID
    import prov

    kwyk = prov.model.Namespace("kwyk", str(KWYKNS))
    niiri = prov.model.Namespace("niiri", str(Constants.NIIRI))
    crypto = prov.model.Namespace("crypto", "http://id.loc.gov/vocabulary/preservation/cryptographicHashFunctions#")
    nidm = prov.model.Namespace("nidm", "http://purl.org/nidash/nidm#")
    from hashlib import sha512
    file_hash = sha512()
    with open(args.stats_file, 'rb') as fp:
        file_hash.update(fp.read())
    stats_e = doc.entity(identifier=niiri[getUUID()],
                         other_attributes={crypto['sha512']: file_hash.hexdigest()})
    kwyk_a = doc.activity(identifier=niiri[getUUID()])
    kwyk_ag = doc.agent(identifier=niiri[getUUID()],
                        other_attributes={prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'],
                                          nidm['NIDM_0000164']: prov.model.Literal("https://github.com/ReproNim/kwyk2nidm", prov.model.XSD_ANYURI),
                                          nidm['NIDM_0000122']: version})
    doc.wasAssociatedWith(kwyk_a, agent=kwyk_ag)
    doc.wasDerivedFrom(e, stats_e, activity=kwyk_a)

    outfile = args.outfile
    if outfile is None:
        outfile = os.path.basename(args.stats_file) + ".ttl"
    doc.serialize(outfile, format="rdf", rdf_format="turtle")
    if args.generate:
        g = create_cde_graph()
        g.serialize("KWYK-NIDM.ttl", format="turtle")


if __name__ == "__main__":
    main()
