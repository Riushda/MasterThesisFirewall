from Cython.Build import cythonize
from setuptools import setup, Extension

# define an extension that will be cythonized and compiled
ext = [Extension(name="lib.handling_queue", sources=["handling_queue.py"]),
       Extension(name="lib.protocol_decoder", sources=["protocol_decoder.py"]),
       Extension(name="lib.mqtt_decoder", sources=["mqtt_decoder.py"]),
       Extension(name="lib.coap_decoder", sources=["coap_decoder.py"]),
       Extension(name="lib.packet_state", sources=["packet_state.py"]),
       Extension(name="lib.abstract_packet", sources=["abstract_packet.py"]),
       Extension(name="lib.constraint_mapping", sources=["relation_mapping.py"])]

ext_options = {"compiler_directives": {"profile": True}, "annotate": True}
setup(ext_modules=cythonize(ext, build_dir="build", language_level="3", **ext_options))
