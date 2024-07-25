import os
from dotenv import load_dotenv
from cad3dify import generate_step_from_2d_cad_image


def main():  
    folder_path = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
    image_filepath = os.path.join(folder_path, 'sample_data/g1-3.jpg')
    output_filepath = os.path.join(folder_path, 'sample_data/gen_result2.step')

    load_dotenv() # .env ファイルを読み込み、環境変数に設定しています。   

    generate_step_from_2d_cad_image(image_filepath, output_filepath)


if __name__ == "__main__":
    main()
