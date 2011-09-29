def initialize(*args, **keywords):
    from core.modules.module_registry import get_module_registry

    from DataCube import CubeReaderHandle, CubeReader

    reg = get_module_registry()
    namespace = "datacube"

    reg.add_module(CubeReaderHandle, namespace=namespace)
    reg.add_module(CubeReader, namespace=namespace)
