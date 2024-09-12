from setuptools import setup, find_packages

setup(
    name="graphe superposer",  # Nom de package valide
    version="1.0.0",
    packages=find_packages(),  # Recherche automatiquement les packages dans ton répertoire
    install_requires=[
        "networkx",
        "matplotlib",
        "pickle"
    ],
    description="A package containing tools for GSEA and clustering on GO terms",
    author="Haladi Ayad, Mike Maillason",
    author_email="crcina.impact.bioinfo@gmail.com",
    url="https://gitlab.univ-nantes.fr/E179974Z/stat_proteo_analysis.git",  # Lien vers le dépôt
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',  # Version de Python minimum requise
)
