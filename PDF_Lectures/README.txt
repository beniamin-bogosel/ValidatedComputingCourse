Expanded PDF lectures for Validated Computing

01  From answers to certificates
02  Floating-point numbers and rounding
03  Conditioning, stability, and cancellation
04  Interval arithmetic as arithmetic with sets
05  Machine intervals and outward rounding
06  Dependency, range bounds, and subdivision

Each PDF targets six A4 pages and a 90-minute session, including discussion,
board calculations, and selected in-class exercises. Remaining exercises and
explicitly optional extensions are for independent practice. Classroom timing
is a proposed teaching plan, not a measured pilot result.

These are expanded lecture notes, not notebook printouts. They add derivations,
worked examples, questions, exact-reference checks, and selected exercise answers.
The corresponding notebooks remain useful for live experiments; Labs 01-06 stay
separate. Python excerpts in Lectures 01-04 use only the standard library.
Lectures 05-06 also use gmpy2 and python-flint from the course environment.
No vc installation is needed to run these excerpts. Within each lecture, run
the code blocks in order in one Python session. The generated plots use NumPy
and Matplotlib.

Editable LaTeX sources and figure-generation code are in source/.
To rebuild from the course root:
    .venv/bin/python PDF_Lectures/build.py

Building requires pdflatex with standard TeX Live packages, Poppler's pdfinfo,
and the course Python environment (NumPy and Matplotlib). The build checks that
each PDF has six pages and no overflowing text boxes. Compilation logs go to build/pdf_lectures/.
The checked-in PDF files can be read without installing any of these tools.

The notes follow the original Lectures 01-06 and cite Tucker and primary sources.
Tucker's examples are explained in original course prose; book pages are not
reproduced. Existing notebooks, Colab setup, release packages, and the material in
Notes2026/ are not modified by this PDF build.
