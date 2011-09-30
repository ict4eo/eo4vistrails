def initialize(*args, **keywords):
    from core.modules.module_registry import get_module_registry

    from DataCube import CubeReaderHandle, ModisCubeReaderHandle, CubeReader, PostGISCubeReader, CubeDateConverter

    reg = get_module_registry()
    namespace = "datacube"

    reg.add_module(CubeReaderHandle, namespace=namespace)
    reg.add_module(ModisCubeReaderHandle, namespace=namespace)
    reg.add_module(CubeReader, namespace=namespace)
    reg.add_module(PostGISCubeReader, namespace=namespace)
    reg.add_module(CubeDateConverter, namespace=namespace)
