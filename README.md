This is the python code for rendering 3D shapes from ShapeNetCore.v1.

Code is slightly modified from intrinsic-networks (https://github.com/JannerM/intrinsics-network) of a paper in NIPS2017 'Self-Supervised Intrinsic Image Decomposition' (http://people.csail.mit.edu/janner/papers/intrinsic_nips_2017.pdf).

My environments:
Ubuntu 18.04

conda create -new <env_name> python=3.6

sudo apt install blender (version 2.79.b)

Change the ./config.py file for the specific settings.

just run:

python run.py --category chair --output output/chair --low 0 --high 100 --repeat 1

check the rendered images in ./dataset/output
