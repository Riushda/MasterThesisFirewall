from Cython.Build import cythonize
from setuptools import setup, Extension

# define an extension that will be cythonized and compiled
ext = [Extension(name="lib.handling_queue", sources=["handling_queue.pyx"]),
       Extension(name="lib.protocol_decoder", sources=["protocol_decoder.pyx"]),
       Extension(name="lib.mqtt_decoder", sources=["mqtt_decoder.pyx"]),
       Extension(name="lib.coap_decoder", sources=["coap_decoder.pyx"]),
       Extension(name="lib.request_state", sources=["request_state.pyx"]),
       Extension(name="lib.abstract_packet", sources=["abstract_packet.pyx"]),
       Extension(name="lib.constraint_mapping", sources=["constraint_mapping.pyx"])]

ext_options = {"compiler_directives": {"profile": True, 'language_level': "3"}, "annotate": True}
setup(ext_modules=cythonize(ext, build_dir="build", **ext_options))
