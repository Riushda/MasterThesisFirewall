from Cython.Build import cythonize
from setuptools import setup, Extension

# define an extension that will be cythonized and compiled
ext = [Extension(name="lib.handling_queue", sources=["handling_queue.pyx"]),
       Extension(name="lib.protocol", sources=["protocol.pyx"]),
       Extension(name="lib.abstract_packet", sources=["abstract_packet.pyx"]),
       Extension(name="lib.constraint_mapping", sources=["constraint_mapping.pyx"])]

ext_options = {"compiler_directives": {"profile": True, 'language_level': "3"}, "annotate": True}
setup(ext_modules=cythonize(ext, build_dir="build", **ext_options))
