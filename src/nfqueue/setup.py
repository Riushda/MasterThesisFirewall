from distutils.core import Extension, setup
from Cython.Build import cythonize

# define an extension that will be cythonized and compiled
ext = [Extension(name="lib.nf_queue", sources=["nf_queue.pyx"]),
       Extension(name="lib.protocol", sources=["protocol.pyx"]),
       Extension(name="lib.abstract_packet", sources=["abstract_packet.pyx"]),
       Extension(name="lib.data_constraint", sources=["data_constraint.pyx"]),
       Extension(name="lib.nf_queue_opti", sources=["nf_queue_opti.pyx"])]

ext_options = {"compiler_directives": {"profile": True}, "annotate": True, 'language_level': "3"}
setup(ext_modules=cythonize(ext, build_dir="build", **ext_options))
