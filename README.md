# Processing point clouds into OBJ/STL files. Surface analysis and morphing of objects.

## Table of Contents
- [About the Project](#about-the-project)
- [Getting Started](#getting-started)
  - [Setup your Environment](#setup-your-environment)
- [Usage](#usage)
- [Documentation](#documentation)
- [Code Examples](#code-examples)



## About the Project

![Static Badge](https://img.shields.io/badge/Python-3.10.13-gray?style=for-the-badge&logo=python&logoColor=yellow&labelColor=black&color=gray)
![Static Badge](https://img.shields.io/badge/Anaconda-3.10-black?style=for-the-badge&logo=anaconda&logoColor=green&labelColor=black&color=gray)
![Static Badge](https://img.shields.io/badge/Open3D-0.18.0-black?style=for-the-badge&logo=open3d&logoColor=green&labelColor=black&color=gray)



[PL]
Projekt ma na celu stworzenie narzędzia do szybkiej identyfikacji wymiarów, kształtów i złożoności obiektów uzyskanych poprzez skanowanie LIDAR. Narzędzie przetworzy chmurę punktów do plików OBJ/STL, wykonując analizę powierzchni i morfizację obiektów. Obsługuje formaty LAZ/LAS, generalizując i segmentując punkty w siatkę, umożliwiając edycję, przemieszczanie, rotację i dodawanie punktów. Dodatkowo pozwala na odczytanie wymiarów płaszczyzn i obiektów na podstawie gotowej siatki.

[EN]
The project aims to create a tool for the rapid identification of dimensions, shapes, and complexity of objects obtained through LIDAR scanning. The tool will process point clouds into OBJ/STL files, perform surface analysis, and morph objects. It supports LAZ/LAS formats, generalizing and segmenting points into a mesh, allowing for editing, moving, rotating, and adding points. Additionally, it enables the reading of dimensions for surfaces and objects based on the generated mesh.





![image](https://github.com/pawel14011/szal_pawel/assets/88234336/85ceec06-14de-481c-9260-6335eb347fa4)

Main GUI Open3D


## Getting Started
### Setup your Environment:
Instructions for installing and configuring the project.

1. Install [Anaconda](https://www.anaconda.com/download)
2.  Clone repositorium or if you're not into package management, just [download a ZIP](https://github.com/MateuszRumin/PWSZ_3IS_2024_ZPI_P3_G3/archive/refs/heads/main.zip) file.
3. Choose the file named 'env_ambitious_project' and import it into the "Anaconda" environment.
4. If you don't have the "PyCharm" program installed, please download and install it from the official website: [download PyCharm](https://www.jetbrains.com/pycharm/download/download-thanks.html?platform=windows&code=PCC).
5. After installation, run the PyCharm program.
6. Select the Python interpreter as an external library for the "env_ambitious_project".

Thanks to the external library, you don't need to download the packages used in the project.
After completing each of the above steps, you should be able to run the main file "main.py" located in the project.

## Usage

Description of how to use the project, usage examples, etc.

## Przykłady

Przykłady użycia lub kodu, aby ułatwić zrozumienie projektu.

## Documentation
Documentation edit: https://www.overleaf.com/read/phdhpkpsdrtz#dd7b5a

Documentation preview: https://www.overleaf.com/3296276632yzbrygbrswrq#2b2940


## Code Examples

```python
# Example Python code
def hello_world():
    print("Hello, World!")

hello_world()
