#!/usr/bin/env python3
"""
Test neuron utils.

File: tests/neuron/test_neuron_utils.py

Copyright 2022 NeuroML contributors
"""


import unittest
import logging
import tempfile
import pathlib
import subprocess
import pytest
from _pytest.monkeypatch import MonkeyPatch


from pyneuroml.neuron import load_hoc_or_python_file, morphinfo, get_utils_hoc
from pyneuroml.pynml import execute_command_in_dir


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class TestNeuronUtils(unittest.TestCase):

    """Test Neuron Utils"""

    def test_hoc_loader(self):
        """Test hoc loader util function"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".hoc") as f:
            print(
                """
                print "Empty test hoc file"
                """,
                file=f,
                flush=True,
            )

            self.assertTrue(load_hoc_or_python_file(f.name))

        with tempfile.NamedTemporaryFile(mode="w", suffix=".hoc") as f:
            print(
                """
                a line that should cause a syntax error
                """,
                file=f,
                flush=True,
            )

            self.assertFalse(load_hoc_or_python_file(f.name))

        # loading python files is not yet implemented
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py") as f:
            print(
                """
                print("An empty test python file")
                """,
                file=f,
                flush=True,
            )

            self.assertFalse(load_hoc_or_python_file(f.name))

    def test_get_utils_hoc(self):
        """Test the get_utils_hoc function"""
        a = get_utils_hoc()
        self.assertTrue(a.is_file())

    """
    The error is probably with mod file compilation. `nrnivmodl` says~:

    Mod files: "mod/mod/CaDynamics_E2.mod" "mod/mod/Ca_HVA.mod"
    "mod/mod/Ca_LVAst.mod" "mod/mod/epsp.mod" "mod/mod/Ih.mod" "mod/mod/Im.mod"
    "mod/mod/K_Pst.mod" "mod/mod/K_Tst.mod" "mod/mod/Nap_Et2.mod"
    "mod/mod/NaTa_t.mod" "mod/mod/NaTs2_t.mod" "mod/mod/SK_E2.mod"
    "mod/mod/SKv3_1.mod"

    The directory "mod" is provided twice here, which is fishy. Running it all
    manually seems to work, so this is very odd.
    """

    # @pytest.mark.skip(
    #     "NEURON works on a local install, but segfaults in a virtual environment"
    # )
    def test_morph_proc(self):
        """Test the morph proc wrapper"""
        # monkeypatch = MonkeyPatch()
        # compile mods
        thispath = pathlib.Path(__file__)
        dirname = str(thispath.parent / pathlib.Path("test_data"))
        # monkeypatch.chdir(dirname)
        # print(dirname)
        # execute_command_in_dir("nrnivmodl mod", ".")
        subprocess.run(["nrnivmodl", dirname + "/mods"])
        # must be done after mod files have been compiled
        from neuron import h

        retval = load_hoc_or_python_file(f"{dirname}/olm.hoc")
        self.assertTrue(retval)
        h("objectvar acell")
        h("acell = new olm()")
        allsections = list(h.allsec())
        logger.debug(f"All sections are: {allsections}")
        # default section is soma_0
        soma_morph = morphinfo(doprint="json")
        self.assertEqual(soma_morph["nsegs"], 1)
        self.assertEqual(soma_morph["n3d"], 3)
        self.assertEqual(soma_morph["3d points"][0]["diam"], 10.0)
        self.assertEqual(soma_morph["3d points"][1]["diam"], 10.0)
        self.assertEqual(soma_morph["3d points"][2]["diam"], 10.0)

        axon_morph = morphinfo("olm[0].axon_0", doprint="json")
        self.assertEqual(axon_morph["nsegs"], 1)
        self.assertEqual(axon_morph["n3d"], 3)
        self.assertEqual(axon_morph["3d points"][0]["diam"], 1.5)
        self.assertEqual(axon_morph["3d points"][1]["y"], -75.0)
        self.assertEqual(axon_morph["3d points"][2]["y"], -150.0)

        dend_morph = morphinfo("olm[0].dend_0", doprint="json")
        self.assertEqual(dend_morph["nsegs"], 1)
        self.assertEqual(dend_morph["n3d"], 3)
        self.assertEqual(dend_morph["3d points"][0]["diam"], 3.0)
        self.assertEqual(dend_morph["3d points"][1]["y"], 120.0)
        self.assertEqual(dend_morph["3d points"][2]["y"], 197.0)
