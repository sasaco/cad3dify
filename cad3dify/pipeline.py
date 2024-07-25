import tempfile

from loguru import logger

from .agents import execute_python_code
from .chains import CadCodeGeneratorChain, CadCodeRefinerChain
from .image import ImageData
from .render import render_and_export_image


def index_map(index: int) -> str:
    if index == 0:
        return "1st"
    elif index == 1:
        return "2nd"
    elif index == 2:
        return "3rd"
    else:
        return f"{index + 1}th"

def generate_step_from_2d_cad_image(image_filepath: str, output_filepath: str, num_refinements: int = 3):
    """Generate a STEP file from a 2D CAD image

    Args:
        image_filepath (str): Path to the 2D CAD image
        output_filepath (str): Path to the output STEP file
    """
    image_data = ImageData.load_from_file(image_filepath)

    # 2DのCAD画像を'cadquery'というpythonのCADライブラリを用いて、3DのCADモデルに変換するコードを生成し
    # 生成した3Dモデルは`cadquery.exporters.export`関数を使ってSTEPファイルで出力
    chain = CadCodeGeneratorChain()

    result: str = chain.invoke(image_data)["result"]
    code = result.format(output_filename=output_filepath) # {output_filename}の部分をoutput_filepathに置き換える
    logger.info("1st code generation complete. Running code...")
    logger.debug("Generated 1st code:")
    logger.debug(code)
    output = execute_python_code(code) # LLMエージェントにコードが正常に実行されるように修正
    logger.debug(output)


    # 3DのCADモデルから得られる3Dビューの画像と2DのCAD画像を比較し、
    # CADモデルを修正するためのコード修正を行う
    refiner_chain = CadCodeRefinerChain()

    # num_refinements回 コード修正を行う
    for i in range(num_refinements):
        path = "tmp/render_and_export_image.png"
        render_and_export_image(output_filepath, path) # 3DのCADモデルを3Dビューの画像に変換する
        logger.info(f"Temporarily rendered image to {path}")
        rendered_image = ImageData.load_from_file(path)
        result = refiner_chain.invoke({
            "code": code, 
            "original_input": image_data, 
            "rendered_result": rendered_image,
            "rendered_image_type": rendered_image.type,
            "rendered_image_data": rendered_image.data,
            "original_image_data": image_data.data,
            "original_image_type": image_data.type
        })["result"]
        code = result.format(output_filename=output_filepath)
        logger.info("Refined code generation complete. Running code...")
        logger.debug(f"Generated {index_map(i)} refined code:")
        logger.debug(code)
        output = execute_python_code(code)
        logger.debug(output)
