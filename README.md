# Processing point clouds into OBJ/STL files. Surface analysis and morphing of objects.

## Table of Contents
- [About the Project](#about-the-project)
- [Getting Started](#getting-started)
  - [Setup your Environment](#setup-your-environment)
- [Main function in the program](#main-function-in-the-program)
  - [Adding a new element to the gui](#ii-adding-a-new-element-to-the-gui)
- [Documentation](#documentation)




## About the Project

![Static Badge](https://img.shields.io/badge/Python-3.10.13-gray?style=for-the-badge&logo=python&logoColor=yellow&labelColor=black&color=gray)
![Static Badge](https://img.shields.io/badge/Anaconda-3.10-black?style=for-the-badge&logo=anaconda&logoColor=green&labelColor=black&color=gray)
![Static Badge](https://img.shields.io/badge/Open3D-0.18.0-black?style=for-the-badge&logo=open3d&logoColor=green&labelColor=black&color=gray)



[PL]
Projekt ma na celu stworzenie narzędzia do szybkiej identyfikacji wymiarów, kształtów i złożoności obiektów uzyskanych poprzez skanowanie LIDAR. Narzędzie przetworzy chmurę punktów do plików OBJ/STL, wykonując analizę powierzchni i morfizację obiektów. Obsługuje formaty LAZ/LAS, generalizując i segmentując punkty w siatkę, umożliwiając edycję, przemieszczanie, rotację i dodawanie punktów. Dodatkowo pozwala na odczytanie wymiarów płaszczyzn i obiektów na podstawie gotowej siatki.

[EN]
The project aims to create a tool for the rapid identification of dimensions, shapes, and complexity of objects obtained through LIDAR scanning. The tool will process point clouds into OBJ/STL files, perform surface analysis, and morph objects. It supports LAZ/LAS formats, generalizing and segmenting points into a mesh, allowing for editing, moving, rotating, and adding points. Additionally, it enables the reading of dimensions for surfaces and objects based on the generated mesh.





![image](https://lh3.googleusercontent.com/fife/ALs6j_FbX1NBNGwgazGu4gD4IoCNGGeLHW5wDDJsWDI8aplwjkjI3RvdxTof8U0cveHQl6-YvCMfE0HFBDeuAoPBGtsgEIXafmH4cwpcX_GPDScRqiEZjFCPDTRnS61HsMM8jzPdDnZ4t702lkiH3JUGEjDY8rpEII-JNEQpiE-t24sRC86NH1ijy3SiOZE_-anEDhj2qljQg5vcc8l3n0CZn1WdVT3W-VWl0bT6PG2imnqPDj0NAh2rU2GeLNo_ECQ26gqdjhZWQmo20a4QnK4AYQ7q0LAe6FCtj0WDizX1puDsuS2gU9_UGmAMzoFjV68ZHl382AgJU-zwx6y_y6G-ipJJo3JGCcpCBGBaxdPTnFHH2cWIhwjh5KyjxucMnRxh7gnKK-QxhKgm6oRZY2v47GfTeCmVdDBzvIIey1L2201dOKMyJvuekNDaA2mX1OonoZBKkGN_wCSSpghrGtwpWV-iQgYY3gYuHcwdSddB_jlMEnzGGIiOeYXW-nbqiPwcN_0BggPKhhJoSLFkmw0p-l4i3uEsgdYal0A41l6NUoDq0zPUV9tuQXmn1NKqgFZPa7K_jXDzr5UNMIF5iuOw5vJ0F7mld8GzLroXupL4Vz44xGaoTlwt3nzRfa8BmQCeBKKBkwqGcQ1eKCCE5m36lUPAJllabTwG3J9Dj0MFCI1PvxWY63SrjuMlA3AQxHMXUC0rB3-OUWcEvZq8Hg3lUuI5FMnvEkrZAVBeu91oNx0YqJe-_oeLBAsu4DcKcaac52qxIdwNYHpNulYUvPnWbQES75Lhtj8qhaZcGNYeZNEUr16LSUCeWRRZv9Wm8Ksg93yZcjvXsf1gUJ5DbaU2BMpvMB0cuurH05hEfKVtQDNmPfyhdkYc0AaRoHhRA1q8bx62W_nEiBIiPAwXo2KZ8sre3g0XDSHZgOlBL-Ro7BNBhsuWeJva-SQqNFn3cWZ5wMZmCUVjKwcMK-wcbEJPqbFQO2Dfc7ccyrMypKk_ZcMLQJTFUSsGci6PTdnTcmqZzNLG1r4-ACu8NXdXeaF1vSzSCSbcJXHcEvE5ozStlk-jxWqJQrkNBzD4hgygRnRftCGcRX3vw0wrKLInMyYOIoFiVhpAsvVwZrNu4VhIe4mu7QEQ-PgXqQZZrpPP5vYR7EzMhY3FhAouqBe17ll7_QR_DVgpHDFfEgR0xairOzP5_tkEZbk2keKiq-IPu7aljcb0_sNc31wNRwrM0M9YHfpm62qAl_llesc0Ptde6cr3r5D6NTRi762gH1BcWXeKUcg_VzzgYplV6LRhZEDEx7mHkBOUj0OQ8evj6bqQO0fIIKtA0-2LmXEF_qK0tJNlefLfMX0oV3e1nC7varGFnZNNxzFMme-n_1uFZOqXyOjzZ9QVFW3hjxgcUaDJWrtqoK5yQ1QFgNizU3wewsKDYCi7CNmP_3wosLyyL-er3dFBZfBQrWCRdCO0JEwMZ8eAgai-a8XH9y1L-EUDgqOv6KJTgIs-QCYWC7kUlpH5JZYHK76cy4KkntX2AJ_e90KIPqQ45sX4wHO4B8lgZxp3Iu1_b1vzGKf9fbRqD-ko1bXiW7ZItbsfNrn1dFEjLBPha8CiztZ8TWZONQ1sOX5AGgoL1AmtPZZSCKnpP_wcLxL2g9PeGRPVFg=w1920-h912)

Main GUI in PyQt5


## Getting Started
### Setup your Environment:
Instructions for installing and configuring the project.

1. Install [Anaconda](https://www.anaconda.com/download)
2. Clone repositorium or if you're not into package management, just [download a ZIP](https://github.com/MateuszRumin/PWSZ_3IS_2024_ZPI_P3_G3/archive/refs/heads/main.zip) file.
3. Choose the file named 'env_ambitious_project' and import it into the "Anaconda" environment.
4. If you don't have the "PyCharm" program installed, please download and install it from the official website: [download PyCharm](https://www.jetbrains.com/pycharm/download/download-thanks.html?platform=windows&code=PCC).
5. After installation, run the PyCharm program.
6. Select the Python interpreter as an external library for the "env_ambitny_project".

After completing each of the above steps, you should be able to run the main file "main.py" located in the project.

## Main function in the program


### II. Adding a new element to the gui

   
## Documentation
Documentation edit: https://www.overleaf.com/read/phdhpkpsdrtz#dd7b5a

Documentation preview: https://www.overleaf.com/3296276632yzbrygbrswrq#2b2940


