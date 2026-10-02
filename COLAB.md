# Running the course in Google Colab

The course notebooks run in both local Jupyter and Google Colab. Every original notebook, including `notebooks/00_setup.ipynb`, has a Colab setup cell before its first course import. Colab runs the course material without installing Python or Jupyter on your computer. `vc` is this course's helper package, not a package to fetch with `pip install vc`. The setup cell loads its Python code from the supplied `vc_runtime.zip` and installs the numerical libraries into the runtime.

## Start a notebook

1. Use the notebooks in this course folder, or extract a current student edition ZIP. Keep the supplied **vc_runtime.zip** beside the course folders. Instructors can use the instructor edition, which includes solutions.
2. Open [Google Colab](https://colab.research.google.com/). Choose **File → Upload notebook** and select `notebooks/00_setup.ipynb` from the course folder.
3. Use a CPU Python runtime with Python 3.12 or newer. No GPU or TPU is needed.
4. Run the **Google Colab setup** cell near the top. When it prompts for a file, select the small **vc_runtime.zip** in the extracted course folder. Do not upload the entire course ZIP at that prompt.
5. Run the remaining setup notebook cells, including the arithmetic and plotting checks. Then open any lecture or lab in the same way.

Each original and exported notebook has its own setup cell. Outside Colab, it leaves the installed local environment unchanged. If you previously uploaded a notebook without this cell, upload the updated file again; the old Colab copy will not acquire the new cell. A new runtime needs setup and upload again; re-running setup in the same runtime reuses the uploaded helper archive. The hash check catches a companion archive from the wrong course version. If Colab reports a conflicting imported package after installation, restart the session and run setup first.

In labs and the project, complete the cells marked as exercises before running their diagnostics. Their deliberate `NotImplementedError` stubs are unfinished student tasks, not Colab installation failures. Lecture and instructor solution notebooks can run in full.

## Save your work

Save a copy of your notebook in Google Drive, or download the edited `.ipynb` before leaving. No Drive mounting is required by the course. Colab runtime storage is temporary and custom files/libraries are not stored with a shared notebook; see the [official Colab FAQ](https://research.google.com/colaboratory/faq.html).

The mirror project writes certificates under `/content/validated-course/build/certificates/`. Download generated JSON files separately using Colab's Files panel. Saving a notebook does not save those runtime files.

Relative links between course notebooks work in local Jupyter, but do not automatically open sibling notebooks in Colab. Use **File → Upload notebook** to select another notebook from the extracted course folder. The regular course edition supplies the syllabus, rubric, references, and browser reading copies; use it alongside the Colab edition.

## Numerical environment

The setup cell pins `gmpy2==2.3.1` and `python-flint==0.9.0`, the arithmetic bindings used for the reviewed course. It accepts Colab's existing NumPy and Matplotlib when they meet the course's minimum versions, and installs Jupytext for the setup notebook's environment report. It does not install JupyterLab or apply the entire Linux authoring lock file to Colab. Internet access is required for the setup installation.

The setup notebook reports the actual Python, numerical package, and native arithmetic library versions. Keep that output with submitted computations. Colab's runtime image can change; passing the arithmetic smoke checks is necessary before continuing. The companion ZIP contains the same public `vc` source supplied with the local course, without worked solutions or book PDFs.

## For the instructor

After editing and synchronizing paired sources, refresh the shared setup cells and companion ZIP, execute the notebooks locally, then export:

```bash
python -m scripts.colab --prepare-sources
python scripts/notebooks.py execute
python -m scripts.colab
```

Outputs are `dist/validated-computing-1.0.0-rc1-colab-student.zip` and `dist/validated-computing-1.0.0-rc1-colab-instructor.zip`. Distribute only the student edition to students, together with the regular student course edition. Regenerate the Colab editions whenever a notebook or `vc` changes. Colab copies have no paired `.py` file; edit the original paired sources to maintain the course, and regenerate the exports. Student submissions can be edited directly in Colab.

The export keeps explanations, exercise tags, and the existing setup cell, and clears outputs so local results are not presented as Colab results. The upload/ZIP-import workflow and exported notebook computations are tested locally with Colab's upload interface simulated. **An actual Google-hosted Colab session has not been tested here.** Before classroom use, run `00_setup.ipynb` and the mirror example in the hosted runtime you intend to use.
