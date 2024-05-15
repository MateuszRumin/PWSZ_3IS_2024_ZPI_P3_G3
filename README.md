# Processing point clouds into OBJ/STL files. Surface analysis and morphing of objects.

## Table of Contents
- [About the Project](#about-the-project)
- [Getting Started](#getting-started)
  - [Setup your Environment](#setup-your-environment)
- [Main function in the program](#main-function-in-the-program)




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
3. Choose the file named 'morph' and import it into the "Anaconda" environment.
4. If you don't have the "PyCharm" program installed, please download and install it from the official website: [download PyCharm](https://www.jetbrains.com/pycharm/download/download-thanks.html?platform=windows&code=PCC).
5. After installation, run the PyCharm program.
6. Select the Python interpreter as an external library for the "morph".

After completing each of the above steps, you should be able to run the main file "main.py" located in the project.
The program mainly uses the pywt5 open3d, pyvista, and numpy libraries.

## Main function in the program
![image](https://lh3.googleusercontent.com/fife/ALs6j_FVwEwSn9d6z7EK9ZZ5CjCf3N8XfRCHfaxdHORpdRgoOvgPtZcipZo8hxXPJ4cVNLrj0wApiSqz0nzrJaBYRnKWaEO-Kyv1iKv6dUNnrd4Dv1eyecQzOW4lIO39q5yddWCpBwBahJF0einTtjL1WR-D6Nqsx0eYKjR1jiXWw_21D9DhDx3MIIKimawR4eAHDeSddyF2O1P92xp2nHUFOT1-sHl_FDaTdE2fS771ZswYGgzYnmy5NlMW5PVBfyfNSAfWpsRUq9WZtW7eTcx-cI85nwtdsnP3DpY6ZG1ZT-l9l7Z5SZLra9_4ISwF-hBoIYAtwNWmrEGLSWfMHjJ3YQC9CF2CBSNEDOeqGjbgJ9LYAZY3r2HejUHQxhjEeCLvFJRRTp30ZVIYDG0RkAtf1r3H7pqnPRJCs_5Enpv4oo_FUa9ANXb0iE1GXAHrT1hHmsvJ8TPzWscGgdZ200QVnHMLAUsBMGVMF5V3A3WzwyTJx-nrto7lY-J96LqBp0WoEJJkq5N5VqCUFHYHtLXUnpFHrMHylWWjoQK1frff2eX545B5usPbqDygib3xDhI2taNz-MhRqEdKDOQjBGSXrd3y2XPBGUpWq60PAbgI6ZXXK1V-VIFnAwxnGKcUmlAX_C-7BPpJFXlUHrkl9v3wdtuFexJqj0x4hf64w36AhzyjOpu9ybqd3NY0jyK0yb188rAfRDZNdKIJ5v4ElxN_Mj60EVWQzgqk3XkYgHm9V_PqvBSFBFZk6hh5fyaAHXBMTB7rzu0mPw1riNey-TnSslO3ZcDQjk2684UmKkumWXceA4jYFdi4d7gvyK7MxRQmivW5NwgedEbV3DNwIT_cHbYq_h8LVWxAma8AgnLwdUwYThjwxF5k_Rb9SdOtGs9ROgqaVkKE3asq4_7KArcUIuE8Qwi51yFZjYHPcvrEeWHUC_W1SKtG17256XourgJHMvB8vUi4JZJqTN0c6oiUTzEFcYOxRxuQn4CYULjQzyQCc2GlSVqS1Yj_VsuMJf9T5HZSx4TAPn2e_NsZgQ0YKxzdBbxpNzZzFpoovjDSbSOGDQg_r4O5hpbzW1ObW_pwX6VeZmWTtVSguNC1PgvXwBj2LPsrthExAFiNComxcIVS53K8olfV1axgS9qnrrJ95UkwO8GFdjDpcvFA5iX0k9YJ-3srRZ307ZMzgCbpgHbHSWlbjmFgkMyCN_zdSWa4e4qsZmtYe1-TSD2iH4kTDclX4vleR1u7srcLlN8RAwfxFFt5WKCIcR_6tDRPcZJFFC4IFnDM2ZbwZfAOFr0CaS1yyrDrNsMs_bKwpbQKSko4HYtG54-Z22Ag7Iqc5_oAW4ZtTJmNSTX4zAexINcYYwXhAWsRyhIAfZqV4R0TZ1VPBxko3vLm14pcgFTRZkeDw4CBZJ1h_thivdRzSHJ-Bj0ICWwgY0t5tQvlBntad96vEBf3aDz_n2DA7OOaVW7-m5B960BCMTTeBJLttZ8-oXhM746-pL53wSN3ZmKryPJS94gnI4Xsuv01aeKtNNsG--BLuTgM5_kvodAxzkvc_XOEVlqq_H1fnsJDF__fbfRN-f5IPdFycocuiRSabEmI8jYSkQ3YtBbDEno5T56YZt5cRGCBnsE517eiDCzOq3wjcBze4R7S=w1920-h912)
| Function | Description |
| --- | --- |
| Create mesh | Creating a mesh from a point cloud with appropriate normals |
| Mesh repair | Filling holes in the mesh and modifying it and removing fragments |
| Removing points | Deleting selected points in a point cloud |
| Model transformations | Reposition, scale and rotate the grid and cloud |
| Mesh calculation | Calculating area and volume in a mesh |
| Isolation fragments | Isolation of clouds and mesh fragments. |
| Triangle reduction | Reducing the number of triangles in the mesh |
| Division of triangles | Dividing the mesh into more smaller triangles |
| Mesh smoothing | Smoothing the mesh by softening the edges |



